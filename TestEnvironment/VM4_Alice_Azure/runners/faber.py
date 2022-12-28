import asyncio
import json
import logging
import os
import sys
import time
import datetime
import requests
from urllib.parse import urlparse
from requests import get
from requests.structures import CaseInsensitiveDict

from aiohttp import ClientError
from qrcode import QRCode

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runners.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from runners.support.agent import (  # noqa:E402
    CRED_FORMAT_INDY,
    CRED_FORMAT_JSON_LD,
    SIG_TYPE_BLS,
    DEFAULT_EXTERNAL_HOST,
)
from runners.support.utils import (  # noqa:E402
    log_msg,
    log_status,
    prompt,
    prompt_loop,
)


CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"
SELF_ATTESTED = os.getenv("SELF_ATTESTED")
TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


class FaberAgent(AriesAgent):
    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        endorser_role: str = None,
        revocation: bool = False,
        **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="Faber",
            no_auto=no_auto,
            endorser_role=endorser_role,
            revocation=revocation,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.transferee_who = None
        self.transferee_connectionid = None
        self.cred_def_id = None
        self.pres_ex_id = None
        self.zkp = False
        self._zkpthreshold= 0 # Here
        self.cred_state = {}
        # TODO define a dict to hold credential attributes
        # based on cred_def_id
        self.cred_attrs = {}

    def get_x(self):
        return self._zkpthreshold
    def set_x(self,value):
        self._zkpthreshold=value


    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    async def handle_present_proof_v2_0(self, message):
        state = message.get("state")
        pres_ex_id = message["pres_ex_id"]
        self.log(f"Presentation: state = {state}, pres_ex_id = {pres_ex_id}")

        if state == "request-received":
            # prover role
            log_status(
                "#24 Query for credentials in the wallet that satisfy the proof request"
            )
            pres_request_indy = message["by_format"].get("pres_request", {}).get("indy")
            pres_request_dif = message["by_format"].get("pres_request", {}).get("dif")

            if pres_request_indy:
                # include self-attested attributes (not included in credentials)
                creds_by_reft = {}
                revealed = {}
                self_attested = {}
                predicates = {}

                try:
                    # select credentials to provide for the proof
                    creds = await self.admin_GET(
                        f"/present-proof-2.0/records/{pres_ex_id}/credentials"
                    )
                    if creds:
                        if "timestamp" in creds[0]["cred_info"]["attrs"]:
                            sorted_creds = sorted(
                                creds,
                                key=lambda c: int(c["cred_info"]["attrs"]["timestamp"]),
                                reverse=True,
                            )
                        else:
                            sorted_creds = creds
                        for row in sorted_creds:
                            for referent in row["presentation_referents"]:
                                if referent not in creds_by_reft:
                                    creds_by_reft[referent] = row

                    # submit the proof wit one unrevealed revealed attribute
                    revealed_flag = False
                    for referent in pres_request_indy["requested_attributes"]:
                        if referent in creds_by_reft:
                            revealed[referent] = {
                                "cred_id": creds_by_reft[referent]["cred_info"][
                                    "referent"
                                ],
                                "revealed": True,
                                #"revealed": revealed_flag, difference between versions resulting in diff proof result
                            }
                            revealed_flag = True
                        else:
                            self_attested[referent] = "my self-attested value"

                    for referent in pres_request_indy["requested_predicates"]:
                        if referent in creds_by_reft:
                            predicates[referent] = {
                                "cred_id": creds_by_reft[referent]["cred_info"][
                                    "referent"
                                ]
                            }

                    log_status("#25 Generate the proof")
                    request = {
                        "indy": {
                            "requested_predicates": predicates,
                            "requested_attributes": revealed,
                            "self_attested_attributes": self_attested,
                        }
                    }
                except ClientError:
                    pass

            elif pres_request_dif:
                try:
                    # select credentials to provide for the proof
                    creds = await self.admin_GET(
                        f"/present-proof-2.0/records/{pres_ex_id}/credentials"
                    )
                    if creds and 0 < len(creds):
                        creds = sorted(
                            creds,
                            key=lambda c: c["issuanceDate"],
                            reverse=True,
                        )
                        record_id = creds[0]["record_id"]
                    else:
                        record_id = None

                    log_status("#25 Generate the proof")
                    request = {
                        "dif": {},
                    }
                    # specify the record id for each input_descriptor id:
                    request["dif"]["record_ids"] = {}
                    for input_descriptor in pres_request_dif["presentation_definition"][
                        "input_descriptors"
                    ]:
                        request["dif"]["record_ids"][input_descriptor["id"]] = [
                            record_id,
                        ]
                    log_msg("presenting ld-presentation:", request)

                    # NOTE that the holder/prover can also/or specify constraints by including the whole proof request
                    # and constraining the presented credentials by adding filters, for example:
                    #
                    # request = {
                    #     "dif": pres_request_dif,
                    # }
                    # request["dif"]["presentation_definition"]["input_descriptors"]["constraints"]["fields"].append(
                    #      {
                    #          "path": [
                    #              "$.id"
                    #          ],
                    #          "purpose": "Specify the id of the credential to present",
                    #          "filter": {
                    #              "const": "https://credential.example.com/residents/1234567890"
                    #          }
                    #      }
                    # )
                    #
                    # (NOTE the above assumes the credential contains an "id", which is an optional field)

                except ClientError:
                    pass

            else:
                raise Exception("Invalid presentation request received")

            log_status("#26 Send the proof to X: " + json.dumps(request))
            await self.admin_POST(
                f"/present-proof-2.0/records/{pres_ex_id}/send-presentation",
                request,
            )

        elif state == "presentation-received":
            # verifier role
            log_status("#27 Process the proof provided by X")
            log_status("#28 Check if proof is valid")
            proof = await self.admin_POST(
                f"/present-proof-2.0/records/{pres_ex_id}/verify-presentation"
            )
            exchange_tracing = False
            verified=proof['verified']
            self.log("** Proof =", proof["verified"])
            self.log("verified=", verified, ", type(verified)=",type(verified))
            self.log("self.zkp=", self.zkp, ",  type(self.zkp)=",type(self.zkp))
            self.last_proof_received = proof
            self.log("self=",self)
            self.log("self.transferee=",self.transferee_who)
            self.log("self.transferee_connectionid=",self.transferee_connectionid)
            self.log("self.pres_ex_id=",self.pres_ex_id)
            self.log("self.zkp=",self.zkp)
            self.log("self.aip=",self.aip)
            self.log("current self.connection_id=",self.connection_id)
            self.log("self.cred_type=",self.cred_type)
            #date=proof['by_format']['pres']['indy']['requested_proof']['revealed_attrs']['0_date_uuid']['raw']
            kwh=proof['by_format']['pres']['indy']['requested_proof']['revealed_attrs']['0_kwh_uuid']['raw']
            #name=proof['by_format']['pres']['indy']['requested_proof']['revealed_attrs']['0_name_uuid']['raw']
            #namex=proof['by_format']['pres_request']['indy']['requested_attributes']['0_name_uuid']['name']
            #datex=proof['by_format']['pres_request']['indy']['requested_attributes']['0_date_uuid']['name']
            #degreex=proof['by_format']['pres_request']['indy']['requested_attributes']['0_degree_uuid']['name']
            #self.log(namex,": ",name,", ",datex,": ",date,", ",degreex,": ",degree)
            if (self.cred_def_id==None):
               self.cred_def_id=proof['by_format']['pres']['indy']['identifiers'][0]['cred_def_id']
            self.log("self.cred_def_id=",self.cred_def_id) #stopping here

            log_status("#28a Issue credential offer to X")
            if (self.zkp and verified=="true"): # here, on contruction, logical if self.zkp at end or self=="12345"
                self.log("***1 here we are")
                connectionid=self.connection_id
                self.connection_id=self.transferee_connectionid
                if self.aip == 10:
                    offer_request = self.generate_credential_offer(
                        self.aip, None, self.cred_def_id, exchange_tracing, self.zkp, None,
                    )
                    await self.agent.admin_POST(
                        "/issue-credential/send-offer", offer_request
                    )

                elif self.aip == 20:
                    if self.cred_type == CRED_FORMAT_INDY:
                        self.log("***2 here we are")
                        age = 24
                        d = datetime.date.today()
                        birth_date = datetime.date(d.year - age, d.month, d.day)
                        birth_date_format = "%Y%m%d"

                        if self.zkp:
                             self.log("***3 here we are")

                             self.cred_attrs[self.cred_def_id] = {
                             "customer": "Bob Marley",
                             "operator": "Faber",
                             "eval": "123",
                             "kwh": kwh,
                             "timestamp": str(int(time.time())),
                             }

                             #self.cred_attrs[self.cred_def_id] = {
                             #    "name": "Bob Marley",
                             #    "date": "2025-05-29",
                             #    "degree": degree,
                             #    "birthdate_dateint": birth_date.strftime(birth_date_format),
                             #    "timestamp": str(int(time.time())),
                             #}

                        else:

                             self.cred_attrs[self.cred_def_id] = {
                             "customer": "Alice Smith",
                             "operator": "Faber",
                             "eval": "123",
                             "kwh": "100",
                             "timestamp": str(int(time.time())),
                             }

                             #self.cred_attrs[self.cred_def_id] = {
                             #     "name": "Alice Smith",
                             #     "date": "2025-05-28",
                             #     "degree": "Maths",
                             #     "birthdate_dateint": birth_date.strftime(birth_date_format),
                             #     "timestamp": str(int(time.time())),
                             #}

                        self.log("***4 here we are")

                        cred_preview = {
                            "@type": CRED_PREVIEW_TYPE,
                            "attributes": [
                                {"name": n, "value": v}
                                for (n, v) in self.cred_attrs[self.cred_def_id].items()
                            ],
                        }
                        self.log("***5 here we are")

                        offer_request = {
                            "connection_id": self.connection_id,
                            "comment": f"Offer on cred def id {self.cred_def_id}",
                            "auto_remove": False,
                            "credential_preview": cred_preview,
                            "filter": {"indy": {"cred_def_id": self.cred_def_id}},
                            "trace": exchange_tracing,
                        }

                        #offer_request = self.generate_credential_offer(
                        #    self.aip,
                        #    self.cred_type,
                        #    self.cred_def_id,
                        #    exchange_tracing,
                        #    self.zkp, # here, ZKP
                        #    degree, # here, inherited attribute *****
                        #)
                        self.log("***6 here we are")


                    elif self.cred_type == CRED_FORMAT_JSON_LD:                 # Here, Look here credential offer
                        offer_request = generate_credential_offer(
                            self.aip,
                            self.cred_type,
                            None,
                            exchange_tracing,
                            None, # here
                            None, # here
                        )

                    else:
                        raise Exception(
                            f"Error invalid credential type: {self.cred_type}"
                        )

                    self.log("offer_request=",offer_request)
                    await self.admin_POST(
                        "/issue-credential-2.0/send-offer", offer_request
                    )                  

                else:
                    raise Exception(f"Error invalid AIP level: {self.aip}")

                self.connection_id=connectionid  # here, return to original connection_id, Alice´s

                if self.revocation:
                   self.log("revocation entry")
                   #
                   publish=True
                   URL1="http://"+DEFAULT_EXTERNAL_HOST+":8021"+"/issue-credential-2.0/records?connection_id="+self.connection_id
                   r=requests.get(URL1)
                   response_dict=json.loads(r.text)
                   cred_ex_id1=response_dict['results'][0]['indy']['cred_ex_id']
                   cred_rev_id1=response_dict['results'][0]['indy']['cred_rev_id']
                   rev_reg_id1=response_dict['results'][0]['indy']['rev_reg_id']         
                   log_msg("rev_reg_id: ", rev_reg_id1)
                   log_msg("cred_ex_id: ", cred_ex_id1)
                   log_msg("cred_rev_id: ", cred_rev_id1)
                   log_msg("publish: ", publish)
                   #publish = (
                   #    await prompt("Publish now? [Y/N]: ", default="N")
                   #).strip() in "yY"
                   try:
                      await self.admin_POST(
                        "/revocation/revoke",
                        {
                            "connection_id": self.connection_id,
                            "rev_reg_id": rev_reg_id1,
                            "cred_rev_id": cred_rev_id1,
                            "publish": publish,
                        },
                      )
                   except ClientError:
                      pass
                   self.log("***7 here we are, after revocation")
                   #
        elif state == "abandoned":
            log_status("Presentation exchange abandoned")
            self.log("Problem report message:", message.get("error_msg"))


    async def handle_basicmessages(self, message):
        URL="http://"+DEFAULT_EXTERNAL_HOST+":8021/connections"
        r=requests.get(URL)
        resp=json.loads(r.text)
        resp2=list(resp['results'])
        alice_connection_id=''
        bob_connection_id=''
        cred_ex_id=""
        for i in resp2:
            if i['their_label'] == "alice.agent":
               alice_connection_id = i['connection_id']
            if i['their_label'] == "bob.agent":
               bob_connection_id = i['connection_id']

        #self.log("Received message:", message["content"])
        x=message["content"]
        self.log(x)
        connectionid=message["connection_id"]
        self.connection_id = message["connection_id"]
        if(connectionid==alice_connection_id):
          self.transferee_connectionid=bob_connection_id
          self.transferee_who="Bob"
        elif(connectionid==bob_connection_id):
          self.transferee_connectionid=alice_connection_id
          self.transferee_who="Alice"

        self.cred_type = CRED_FORMAT_INDY
        exchange_tracing = False
        #self.log("self=",self)
        #self.log("Before ZKP, connectionid=",connectionid)

        if "ZKP" in x:
           #self.log("* Received message:", message["content"])
           #self.log("* ZKP indication received from holder")
           #self.log("* connectionid: ",connectionid)     

           #self.log("self.aip= ",self.aip)
           #self.log("self.cred_type= ",self.cred_type) # Stopping here
           self.zkp = True
           msg="Faber says ZKP OK"
           await self.admin_POST(
                 f"/connections/{connectionid}/send-message",
                 {"content": msg},
                 )
           if self.aip == 10:
                 proof_request_web_request = (
                     self.generate_proof_request_web_request(
                            self.aip,
                            self.cred_type,
                            self.revocation,
                            exchange_tracing,
                      )
                    )
                 await self.admin_POST(
                        "/present-proof/send-request", proof_request_web_request
                 )
                 pass

           elif self.aip == 20:
                    if self.cred_type == CRED_FORMAT_INDY:
                        #self.log("here we are")
                        #self.log("self.revocation=",self.revocation)
                        proof_request_web_request = (
                            self.generate_proof_request_web_request(
                                self.aip,
                                self.cred_type,
                                self.revocation,
                                exchange_tracing,
                            )
                        )
                        self.log(proof_request_web_request)

                    elif self.cred_type == CRED_FORMAT_JSON_LD:
                        proof_request_web_request = (
                            self.generate_proof_request_web_request(
                                self.aip,
                                self.cred_type,
                                self.revocation,
                                exchange_tracing,
                            )
                        )

                    else:
                         raise Exception(
                         "Error invalid credential type:" + self.cred_type
                         )

                    # Error: self pointer is not correct.
                    # Try: http://20.206.89.102:8021/issue-credential-2.0/send-request
                    #
                    resp=await self.admin_POST(
                          "/present-proof-2.0/send-request", proof_request_web_request
                    )
                    self.pres_ex_id=resp['pres_ex_id']
                    #self.log("* pres_ex_id=",pres_ex_id)
                    
                    # self is wrong pointer
                    #time.sleep(30) # sleep 2 seconds

                    #proof = await self.admin_GET(
                    #   f"/present-proof-2.0/records/{pres_ex_id}"
                    #)
                    #state=proof['state']
                    #self.log("state=",state)

                    # self.log("proof=",proof)
                    # verified=proof["verified"]
                    # self.log("* verified=",verified,"type(verified)=",type(verified))
                    # self.log("* Proof =", proof["verified"])
                    # if(verified=='true'):
                      #self.log("OK transferee=",transferee_who,", transferee_connectionid=",transferee_connectionid)
                    # else:
                      #self.log("NOK transferee=",transferee_who,", transferee_connectionid=",transferee_connectionid)


                    self.connection_id = connectionid


           else:
                    raise Exception(f"Error invalid AIP level: {self.aip}")

        else:
           self.log("Received message:", message["content"])



    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    def generate_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing, zkp, param1):
        self.log("self at generate_credential_offer=",self)
        age = 24
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "Alice Smith",
                "date": "2018-05-28",
                "degree": "Maths",
                "birthdate_dateint": birth_date.strftime(birth_date_format),
                "timestamp": str(int(time.time())),
            }

            cred_preview = {
                "@type": CRED_PREVIEW_TYPE,
                "attributes": [
                    {"name": n, "value": v}
                    for (n, v) in self.cred_attrs[cred_def_id].items()
                ],
            }
            offer_request = {
                "connection_id": self.connection_id,
                "cred_def_id": cred_def_id,
                "comment": f"Offer on cred def id {cred_def_id}",
                "auto_remove": False,
                "credential_preview": cred_preview,
                "trace": exchange_tracing,
            }
            return offer_request

        elif aip == 20:
            if cred_type == CRED_FORMAT_INDY:
                if zkp:
                  self.cred_attrs[cred_def_id] = {
                      "customer": "Bob Marley",
                      "operator": "Faber",
                      "eval": "123",
                      "kwh": param1,
                      #"birthdate_dateint": birth_date.strftime(birth_date_format),
                      "timestamp": str(int(time.time())),
                  }

                  #self.cred_attrs[cred_def_id] = {
                  #    "name": "Bob Marley",
                  #    "date": "2025-05-29",
                  #    "degree": param1,
                  #    "birthdate_dateint": birth_date.strftime(birth_date_format),
                  #    "timestamp": str(int(time.time())),
                  #}

                else:
                  self.cred_attrs[cred_def_id] = {
                      "customer": "Alice Smith",
                      "operator": "Faber",
                      "eval": "123",
                      "kwh": "100",
                      #"birthdate_dateint": birth_date.strftime(birth_date_format),
                      "timestamp": str(int(time.time())),
                  }

                  #self.cred_attrs[cred_def_id] = {
                  #    "name": "Alice Smith",
                  #    "date": "2025-05-28",
                  #    "degree": "Maths",
                  #    "birthdate_dateint": birth_date.strftime(birth_date_format),
                  #    "timestamp": str(int(time.time())),
                  #}


                cred_preview = {
                    "@type": CRED_PREVIEW_TYPE,
                    "attributes": [
                        {"name": n, "value": v}
                        for (n, v) in self.cred_attrs[cred_def_id].items()
                    ],
                }
                offer_request = {
                    "connection_id": self.connection_id,
                    "comment": f"Offer on cred def id {cred_def_id}",
                    "auto_remove": False,
                    "credential_preview": cred_preview,
                    "filter": {"indy": {"cred_def_id": cred_def_id}},
                    "trace": exchange_tracing,
                }
                return offer_request

            elif cred_type == CRED_FORMAT_JSON_LD:
                offer_request = {
                    "connection_id": self.connection_id,
                    "filter": {
                        "ld_proof": {
                            "credential": {
                                "@context": [
                                    "https://www.w3.org/2018/credentials/v1",
                                    "https://w3id.org/citizenship/v1",
                                    "https://w3id.org/security/bbs/v1",
                                ],
                                "type": [
                                    "VerifiableCredential",
                                    "PermanentResident",
                                ],
                                "id": "https://credential.example.com/residents/1234567890",
                                "issuer": self.did,
                                "issuanceDate": "2020-01-01T12:00:00Z",
                                "credentialSubject": {
                                    "type": ["PermanentResident"],
                                    "givenName": "ALICE",
                                    "familyName": "SMITH",
                                    "gender": "Female",
                                    "birthCountry": "Bahamas",
                                    "birthDate": "1958-07-17",
                                },
                            },
                            "options": {"proofType": SIG_TYPE_BLS},
                        }
                    },
                }
                return offer_request

            else:
                raise Exception(f"Error invalid credential type: {self.cred_type}")

        else:
            raise Exception(f"Error invalid AIP level: {self.aip}")

    def generate_proof_request_web_request(
        self, aip, cred_type, revocation, exchange_tracing, connectionless=False
    ):
        #evaluation = input('Type evaluation value for ZPK (e.g. 123): ')
        evaluation = self.get_x()
        log_msg("generate proof self.x or uation=",evaluation)
        eval_int=int(evaluation)

        age = 18
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"
        if aip == 10:
            req_attrs = [
                {
                    "name": "name",
                    "restrictions": [{"schema_name": "degree schema"}],
                },
                {
                    "name": "date",
                    "restrictions": [{"schema_name": "degree schema"}],
                },
            ]
            if revocation:
                req_attrs.append(
                    {
                        "name": "degree",
                        "restrictions": [{"schema_name": "degree schema"}],
                        "non_revoked": {"to": int(time.time() - 1)},
                    },
                )
            else:
                req_attrs.append(
                    {
                        "name": "degree",
                        "restrictions": [{"schema_name": "degree schema"}],
                    }
                )
            if SELF_ATTESTED:
                # test self-attested claims
                req_attrs.append(
                    {"name": "self_attested_thing"},
                )
            req_preds = [
                # test zero-knowledge proofs
                {
                    "name": "birthdate_dateint",
                    "p_type": "<=",
                    "p_value": int(birth_date.strftime(birth_date_format)),
                    "restrictions": [{"schema_name": "degree schema"}],
                }
            ]
            indy_proof_request = {
                "name": "Proof of Education",
                "version": "1.0",
                "requested_attributes": {
                    f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                },
                "requested_predicates": {
                    f"0_{req_pred['name']}_GE_uuid": req_pred for req_pred in req_preds
                },
            }

            if revocation:
                indy_proof_request["non_revoked"] = {"to": int(time.time())}

            proof_request_web_request = {
                "proof_request": indy_proof_request,
                "trace": exchange_tracing,
            }
            if not connectionless:
                proof_request_web_request["connection_id"] = self.connection_id
            return proof_request_web_request

        elif aip == 20:
            if cred_type == CRED_FORMAT_INDY:
                req_attrs = [
                    {
                        "name": "customer",
                        "restrictions": [{"schema_name": "energy schema"}],
                    },
                    {
                        "name": "kwh",
                        "restrictions": [{"schema_name": "energy schema"}],
                    },
                ]
                if revocation:
                    req_attrs.append(
                        {
                            "name": "operator",
                            "restrictions": [{"schema_name": "energy schema"}],
                            "non_revoked": {"to": int(time.time() - 1)},
                        },
                    )
                else:
                    req_attrs.append(
                        {
                            "name": "operator",
                            "restrictions": [{"schema_name": "energy schema"}],
                        }
                    )
                if SELF_ATTESTED:
                    # test self-attested claims
                    req_attrs.append(
                        {"name": "self_attested_thing"},
                    )
                req_preds = [
                    # test zero-knowledge proofs
                    {
                        "name": "eval",
                        "p_type": ">=",
                        "p_value": eval_int,
                        "restrictions": [{"schema_name": "energy schema"}],
                    }
                   #{
                   #     "name": "birthdate_dateint",
                   #     "p_type": "<=",
                   #     "p_value": int(birth_date.strftime(birth_date_format)),
                   #     "restrictions": [{"schema_name": "energy schema"}],
                   # }

                ]
                indy_proof_request = {
                    "name": "Proof of Energy",
                    "version": "1.0",
                    "requested_attributes": {
                        f"0_{req_attr['name']}_uuid": req_attr for req_attr in req_attrs
                    },
                    "requested_predicates": {
                        f"0_{req_pred['name']}_GE_uuid": req_pred
                        for req_pred in req_preds
                    },
                }

                if revocation:
                    indy_proof_request["non_revoked"] = {"to": int(time.time())}

                proof_request_web_request = {
                    "presentation_request": {"indy": indy_proof_request},
                    "trace": exchange_tracing,
                }
                if not connectionless:
                    proof_request_web_request["connection_id"] = self.connection_id
                return proof_request_web_request

            elif cred_type == CRED_FORMAT_JSON_LD:
                proof_request_web_request = {
                    "comment": "test proof request for json-ld",
                    "presentation_request": {
                        "dif": {
                            "options": {
                                "challenge": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                                "domain": "4jt78h47fh47",
                            },
                            "presentation_definition": {
                                "id": "32f54163-7166-48f1-93d8-ff217bdb0654",
                                "format": {"ldp_vp": {"proof_type": [SIG_TYPE_BLS]}},
                                "input_descriptors": [
                                    {
                                        "id": "citizenship_input_1",
                                        "name": "EU Driver's License",
                                        "schema": [
                                            {
                                                "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"
                                            },
                                            {
                                                "uri": "https://w3id.org/citizenship#PermanentResident"
                                            },
                                        ],
                                        "constraints": {
                                            "limit_disclosure": "required",
                                            "is_holder": [
                                                {
                                                    "directive": "required",
                                                    "field_id": [
                                                        "1f44d55f-f161-4938-a659-f8026467f126"
                                                    ],
                                                }
                                            ],
                                            "fields": [
                                                {
                                                    "id": "1f44d55f-f161-4938-a659-f8026467f126",
                                                    "path": [
                                                        "$.credentialSubject.familyName"
                                                    ],
                                                    "purpose": "The claim must be from one of the specified person",
                                                    "filter": {"const": "SMITH"},
                                                },
                                                {
                                                    "path": [
                                                        "$.credentialSubject.givenName"
                                                    ],
                                                    "purpose": "The claim must be from one of the specified person",
                                                },
                                            ],
                                        },
                                    }
                                ],
                            },
                        }
                    },
                }
                if not connectionless:
                    proof_request_web_request["connection_id"] = self.connection_id
                return proof_request_web_request

            else:
                raise Exception(f"Error invalid credential type: {self.cred_type}")

        else:
            raise Exception(f"Error invalid AIP level: {self.aip}")


async def main(args):
    faber_agent = await create_agent_with_args(args, ident="faber")

    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {faber_agent.wallet_type})"
                if faber_agent.wallet_type
                else ""
            )
        )
        agent = FaberAgent(
            "faber.agent",
            faber_agent.start_port,
            faber_agent.start_port + 1,
            genesis_data=faber_agent.genesis_txns,
            genesis_txn_list=faber_agent.genesis_txn_list,
            no_auto=faber_agent.no_auto,
            tails_server_base_url=faber_agent.tails_server_base_url,
            revocation=faber_agent.revocation,
            timing=faber_agent.show_timing,
            multitenant=faber_agent.multitenant,
            mediation=faber_agent.mediation,
            wallet_type=faber_agent.wallet_type,
            seed=faber_agent.seed,
            aip=faber_agent.aip,
            endorser_role=faber_agent.endorser_role,
        )

        faber_schema_name = "energy schema"
        faber_schema_attrs = [
            "customer",
            "operator",
            "eval",
            "kwh",
            "timestamp",
        ]
        if faber_agent.cred_type == CRED_FORMAT_INDY:
            faber_agent.public_did = True
            await faber_agent.initialize(
                the_agent=agent,
                schema_name=faber_schema_name,
                schema_attrs=faber_schema_attrs,
                create_endorser_agent=(faber_agent.endorser_role == "author")
                if faber_agent.endorser_role
                else False,
            )
        elif faber_agent.cred_type == CRED_FORMAT_JSON_LD:
            faber_agent.public_did = True
            await faber_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + faber_agent.cred_type)

        # generate an invitation for Alice
        #await faber_agent.generate_invitation(
        #    display_qr=True, reuse_connections=faber_agent.reuse_connections, wait=True
        #)

        exchange_tracing = False
        options = (
            "    (1) Issue Credential\n"
            "    (2) Send Proof Request\n"
            "    (2a) Send *Connectionless* Proof Request (requires a Mobile client)\n"
            "    (2b) Set up new threshold for ZKP\n"
            "    (2c) Read ZKP threshold\n"
            "    (3) Send Message\n"
            "    (4) Create New Invitation\n"
        )
        if faber_agent.revocation:
            options += "    (5) Revoke Credential\n" "    (6) Publish Revocations\n"
        if faber_agent.endorser_role and faber_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if faber_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
        options += "    (T) Toggle tracing on credential/proof exchange\n"
        options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
            "5/6/" if faber_agent.revocation else "",
            "W/" if faber_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and faber_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await faber_agent.agent.admin_POST(
                    f"/transactions/{faber_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did},
                )

            elif option in "wW" and faber_agent.multitenant:
                target_wallet_name = await prompt("Enter wallet name: ")
                include_subwallet_webhook = await prompt(
                    "(Y/N) Create sub-wallet webhook target: "
                )
                if include_subwallet_webhook.lower() == "y":
                    created = await faber_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        webhook_port=faber_agent.agent.get_new_webhook_port(),
                        public_did=True,
                        mediator_agent=faber_agent.mediator_agent,
                        endorser_agent=faber_agent.endorser_agent,
                        taa_accept=faber_agent.taa_accept,
                    )
                else:
                    created = await faber_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        public_did=True,
                        mediator_agent=faber_agent.mediator_agent,
                        endorser_agent=faber_agent.endorser_agent,
                        cred_type=faber_agent.cred_type,
                        taa_accept=faber_agent.taa_accept,
                    )
                # create a schema and cred def for the new wallet
                # TODO check first in case we are switching between existing wallets
                if created:
                    # TODO this fails because the new wallet doesn't get a public DID
                    await faber_agent.create_schema_and_cred_def(
                        schema_name=faber_schema_name,
                        schema_attrs=faber_schema_attrs,
                    )

            elif option in "tT":
                exchange_tracing = not exchange_tracing
                log_msg(
                    ">>> Credential/Proof Exchange Tracing is {}".format(
                        "ON" if exchange_tracing else "OFF"
                    )
                )

            elif option == "1":
                log_status("#13 Issue credential offer to X")

                if faber_agent.aip == 10:
                    offer_request = faber_agent.agent.generate_credential_offer(
                        faber_agent.aip, None, faber_agent.cred_def_id, exchange_tracing, None, None,
                    )
                    await faber_agent.agent.admin_POST(
                        "/issue-credential/send-offer", offer_request
                    )

                elif faber_agent.aip == 20:
                    if faber_agent.cred_type == CRED_FORMAT_INDY:
                        offer_request = faber_agent.agent.generate_credential_offer(
                            faber_agent.aip,
                            faber_agent.cred_type,
                            faber_agent.cred_def_id,
                            exchange_tracing,
                            None, # here, ZKP
                            None, # here, param1
                        )

                    elif faber_agent.cred_type == CRED_FORMAT_JSON_LD:                 # Here, Look here credential offer
                        offer_request = faber_agent.agent.generate_credential_offer(
                            faber_agent.aip,
                            faber_agent.cred_type,
                            None,
                            exchange_tracing,
                            None, # here, ZKP
                            None, # here, param1
                        )

                    else:
                        raise Exception(
                            f"Error invalid credential type: {faber_agent.cred_type}"
                        )

                    await faber_agent.agent.admin_POST(
                        "/issue-credential-2.0/send-offer", offer_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {faber_agent.aip}")

            elif option == "2":
                log_status("#20 Request proof of degree from alice")
                if faber_agent.aip == 10:
                    proof_request_web_request = (
                        faber_agent.agent.generate_proof_request_web_request(
                            faber_agent.aip,
                            faber_agent.cred_type,
                            faber_agent.revocation,
                            exchange_tracing,
                        )
                    )
                    await faber_agent.agent.admin_POST(
                        "/present-proof/send-request", proof_request_web_request
                    )
                    pass

                elif faber_agent.aip == 20:
                    if faber_agent.cred_type == CRED_FORMAT_INDY:
                        proof_request_web_request = (
                            faber_agent.agent.generate_proof_request_web_request(
                                faber_agent.aip,
                                faber_agent.cred_type,
                                faber_agent.revocation,
                                exchange_tracing,
                            )
                        )

                    elif faber_agent.cred_type == CRED_FORMAT_JSON_LD:
                        proof_request_web_request = (
                            faber_agent.agent.generate_proof_request_web_request(
                                faber_agent.aip,
                                faber_agent.cred_type,
                                faber_agent.revocation,
                                exchange_tracing,
                            )
                        )

                    else:
                        raise Exception(
                            "Error invalid credential type:" + faber_agent.cred_type
                        )

                    await agent.admin_POST(
                        "/present-proof-2.0/send-request", proof_request_web_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {faber_agent.aip}")

            elif option == "2a":
                log_status("#20 Request * Connectionless * proof of degree from alice")
                if faber_agent.aip == 10:
                    proof_request_web_request = (
                        faber_agent.agent.generate_proof_request_web_request(
                            faber_agent.aip,
                            faber_agent.cred_type,
                            faber_agent.revocation,
                            exchange_tracing,
                            connectionless=True,
                        )
                    )
                    proof_request = await faber_agent.agent.admin_POST(
                        "/present-proof/create-request", proof_request_web_request
                    )
                    pres_req_id = proof_request["presentation_exchange_id"]
                    url = (
                        os.getenv("WEBHOOK_TARGET")
                        or (
                            "http://"
                            + os.getenv("DOCKERHOST").replace(
                                "{PORT}", str(faber_agent.agent.admin_port + 1)
                            )
                            + "/webhooks"
                        )
                    ) + f"/pres_req/{pres_req_id}/"
                    log_msg(f"Proof request url: {url}")
                    qr = QRCode(border=1)
                    qr.add_data(url)
                    log_msg(
                        "Scan the following QR code to accept the proof request from a mobile agent."
                    )
                    qr.print_ascii(invert=True)

                elif faber_agent.aip == 20:
                    if faber_agent.cred_type == CRED_FORMAT_INDY:
                        proof_request_web_request = (
                            faber_agent.agent.generate_proof_request_web_request(
                                faber_agent.aip,
                                faber_agent.cred_type,
                                faber_agent.revocation,
                                exchange_tracing,
                                connectionless=True,
                            )
                        )
                    elif faber_agent.cred_type == CRED_FORMAT_JSON_LD:
                        proof_request_web_request = (
                            faber_agent.agent.generate_proof_request_web_request(
                                faber_agent.aip,
                                faber_agent.cred_type,
                                faber_agent.revocation,
                                exchange_tracing,
                                connectionless=True,
                            )
                        )
                    else:
                        raise Exception(
                            "Error invalid credential type:" + faber_agent.cred_type
                        )

                    proof_request = await faber_agent.agent.admin_POST(
                        "/present-proof-2.0/create-request", proof_request_web_request
                    )
                    pres_req_id = proof_request["pres_ex_id"]
                    url = (
                        "http://"
                        + os.getenv("DOCKERHOST").replace(
                            "{PORT}", str(faber_agent.agent.admin_port + 1)
                        )
                        + "/webhooks/pres_req/"
                        + pres_req_id
                        + "/"
                    )
                    log_msg(f"Proof request url: {url}")
                    qr = QRCode(border=1)
                    qr.add_data(url)
                    log_msg(
                        "Scan the following QR code to accept the proof request from a mobile agent."
                    )
                    qr.print_ascii(invert=True)
                else:
                    raise Exception(f"Error invalid AIP level: {faber_agent.aip}")

            elif option == "2b":
                x = await prompt("Enter message new threshold for ZKP (0..): ")
                agent.set_x(x)
                log_msg("ZKP threshold - eval parameter", x)
 
            elif option == "2c":
                log_msg("ZKP threshold - eval parameter", agent.get_x())

            elif option == "3":
                msg = await prompt("Enter message: ")
                await faber_agent.agent.admin_POST(
                    f"/connections/{faber_agent.agent.connection_id}/send-message",
                    {"content": msg},
                )

            elif option == "4":
                log_msg(
                    "Creating a new invitation, please receive "
                    "and accept this invitation using Alice agent"
                )
                await faber_agent.generate_invitation(
                    display_qr=True,
                    reuse_connections=faber_agent.reuse_connections,
                    wait=True,
                )

            elif option == "5" and faber_agent.revocation:
                rev_reg_id = (await prompt("Enter revocation registry ID: ")).strip()
                cred_rev_id = (await prompt("Enter credential revocation ID: ")).strip()
                publish = (
                    await prompt("Publish now? [Y/N]: ", default="N")
                ).strip() in "yY"
                try:
                    await faber_agent.agent.admin_POST(
                        "/revocation/revoke",
                        {
                            "rev_reg_id": rev_reg_id,
                            "cred_rev_id": cred_rev_id,
                            "publish": publish,
                            "connection_id": faber_agent.agent.connection_id,
                            # leave out thread_id, let aca-py generate
                            # "thread_id": "12345678-4444-4444-4444-123456789012",
                            "comment": "Revocation reason goes here ...",
                        },
                    )
                except ClientError:
                    pass

            elif option == "6" and faber_agent.revocation:
                try:
                    resp = await faber_agent.agent.admin_POST(
                        "/revocation/publish-revocations", {}
                    )
                    faber_agent.agent.log(
                        "Published revocations for {} revocation registr{} {}".format(
                            len(resp["rrid2crid"]),
                            "y" if len(resp["rrid2crid"]) == 1 else "ies",
                            json.dumps([k for k in resp["rrid2crid"]], indent=4),
                        )
                    )
                except ClientError:
                    pass

        if faber_agent.show_timing:
            timing = await faber_agent.agent.fetch_timing()
            if timing:
                for line in faber_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await faber_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="faber", port=8020)
    args = parser.parse_args()

    ENABLE_PYDEVD_PYCHARM = os.getenv("ENABLE_PYDEVD_PYCHARM", "").lower()
    ENABLE_PYDEVD_PYCHARM = ENABLE_PYDEVD_PYCHARM and ENABLE_PYDEVD_PYCHARM not in (
        "false",
        "0",
    )
    PYDEVD_PYCHARM_HOST = os.getenv("PYDEVD_PYCHARM_HOST", "localhost")
    PYDEVD_PYCHARM_CONTROLLER_PORT = int(
        os.getenv("PYDEVD_PYCHARM_CONTROLLER_PORT", 5001)
    )

    if ENABLE_PYDEVD_PYCHARM:
        try:
            import pydevd_pycharm

            print(
                "Faber remote debugging to "
                f"{PYDEVD_PYCHARM_HOST}:{PYDEVD_PYCHARM_CONTROLLER_PORT}"
            )
            pydevd_pycharm.settrace(
                host=PYDEVD_PYCHARM_HOST,
                port=PYDEVD_PYCHARM_CONTROLLER_PORT,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
            )
        except ImportError:
            print("pydevd_pycharm library was not found")

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
