import asyncio
import base64
import binascii
import json
import logging
import os
import sys
import requests
import time # here
import datetime # here
from urllib.parse import urlparse
from requests import get
from requests.structures import CaseInsensitiveDict


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runners.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from runners.support.utils import (  # noqa:E402
    check_requires,
    log_msg,
    log_status,
    log_timer,
    prompt,
    prompt_loop,
)

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)

from runners.support.agent import (  # noqa:E402
    CRED_FORMAT_INDY,
    CRED_FORMAT_JSON_LD,
    SIG_TYPE_BLS,
    DEFAULT_EXTERNAL_HOST,
)

class BobAgent(AriesAgent):
    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        aip: int = 20,
        endorser_role: str = None,
        cred_type = CRED_FORMAT_INDY,
        **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="Bob",
            no_auto=no_auto,
            seed=None,
            aip=aip,
            endorser_role=endorser_role,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}
        self.cred_attrs = {}  # Here
        self.proved=False # Here


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
            self.log("*<new>* Proof =", proof["verified"])
            self.last_proof_received = proof

        elif state == "abandoned":
            log_status("Presentation exchange abandoned")
            self.log("Problem report message:", message.get("error_msg"))

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()

    async def handle_basicmessages(self, message):
        #self.log("Bob received message")
        self.log("Received message:", message["content"])


    def generate_credential_offer(self, aip, cred_type, cred_def_id, exchange_tracing):
        age = 24
        d = datetime.date.today()
        birth_date = datetime.date(d.year - age, d.month, d.day)
        birth_date_format = "%Y%m%d"        
        print("cred_type=",cred_type) 
        if aip == 10:
            # define attributes to send for credential
            self.cred_attrs[cred_def_id] = {
                "name": "Bob Marley",
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
            if cred_type == CRED_FORMAT_INDY:  # HERE, CRED_FORMAT_INDY

                URL="http://"+DEFAULT_EXTERNAL_HOST+":8031/credentials"
                #URL='http://20.206.89.102:8031/credentials'
                r=requests.get(URL)
                response_dict=json.loads(r.text)
                serviceurl= ""
                accesstoken=""
                customer=""
                customerid=""
                operator=""
                timestamp=""
                evaluation=""

                if(len(response_dict['results'])!=0):
                   bob_credential=response_dict['results'][0]
                   cred_def_id=bob_credential['cred_def_id']
                   serviceurl=bob_credential['attrs']['serviceurl']
                   accesstoken=bob_credential['attrs']['accesstoken']
                   customer=bob_credential['attrs']['customer'] 
                   customerid=bob_credential['attrs']['customerid']
                   operator=bob_credential['attrs']['operator']    
                   timestamp=bob_credential['attrs']['timestamp']  
                   evaluation=bob_credential['attrs']['eval'] 


                self.cred_attrs[cred_def_id] = {
  			"customer": customer,
			"customerid": customerid,
			"operator": operator,
			"serviceurl": serviceurl,
			"accesstoken": accesstoken,
			"eval": evaluation,
			"timestamp": timestamp,
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
                                    "givenName": "BOB",
                                    "familyName": "MARLEY",
                                    "gender": "Male",
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



async def input_invitation(agent_container):
    agent_container.agent._connection_ready = asyncio.Future()
    async for details in prompt_loop("Invite details: "):
        b64_invite = None
        try:
            url = urlparse(details)
            query = url.query
            if query and "c_i=" in query:
                pos = query.index("c_i=") + 4
                b64_invite = query[pos:]
            elif query and "oob=" in query:
                pos = query.index("oob=") + 4
                b64_invite = query[pos:]
            else:
                b64_invite = details
        except ValueError:
            b64_invite = details

        if b64_invite:
            try:
                padlen = 4 - len(b64_invite) % 4
                if padlen <= 2:
                    b64_invite += "=" * padlen
                invite_json = base64.urlsafe_b64decode(b64_invite)
                details = invite_json.decode("utf-8")
            except binascii.Error:
                pass
            except UnicodeDecodeError:
                pass

        if details:
            try:
                details = json.loads(details)
                break
            except json.JSONDecodeError as e:
                log_msg("Invalid invitation:", str(e))

    with log_timer("Connect duration:"):
        connection = await agent_container.input_invitation(details, wait=True)


async def main(args):
    bob_agent = await create_agent_with_args(args, ident="bob")

    try:
        log_status(
            "#7 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {bob_agent.wallet_type})"
                if bob_agent.wallet_type
                else ""
            )
        )
        agent = BobAgent(
            "bob.agent",
            bob_agent.start_port,
            bob_agent.start_port + 1,
            genesis_data=bob_agent.genesis_txns,
            genesis_txn_list=bob_agent.genesis_txn_list,
            no_auto=bob_agent.no_auto,
            tails_server_base_url=bob_agent.tails_server_base_url,
            revocation=bob_agent.revocation,
            timing=bob_agent.show_timing,
            multitenant=bob_agent.multitenant,
            mediation=bob_agent.mediation,
            wallet_type=bob_agent.wallet_type,
            aip=bob_agent.aip,
            endorser_role=bob_agent.endorser_role,
        )

        await bob_agent.initialize(the_agent=agent)

        #log_status("#9 Input faber.py invitation details")
        #await input_invitation(bob_agent)
        exchange_tracing = False # Here
        cred_type=CRED_FORMAT_INDY



        options = "    (1) Issue Credential\n" "    (3) Send Message \n" "    (4) Input New Invitation\n" "    (5) Generate New Invitation\n" "    (6a) Request Credential Proof\n"
        options += "    (6b) Energy Token Management\n"
        if bob_agent.endorser_role and bob_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if bob_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
        options += "    (X) Exit?\n[3/4/5/6a/6b{}X] ".format(
            "W/" if bob_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and bob_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await bob_agent.agent.admin_POST(
                    f"/transactions/{bob_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did, "endorser_name": "endorser"},
                )

            elif option in "wW" and bob_agent.multitenant:
                target_wallet_name = await prompt("Enter wallet name: ")
                include_subwallet_webhook = await prompt(
                    "(Y/N) Create sub-wallet webhook target: "
                )
                if include_subwallet_webhook.lower() == "y":
                    await bob_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        webhook_port=bob_agent.agent.get_new_webhook_port(),
                        mediator_agent=bob_agent.mediator_agent,
                        taa_accept=bob_agent.taa_accept,
                    )
                else:
                    await bob_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        mediator_agent=bob_agent.mediator_agent,
                        taa_accept=bob_agent.taa_accept,
                    )
            elif option == "1":
                aip = 20
                log_status("#13 Issue credential offer to X: ")
                if aip == 10:
                    offer_request = bob_agent.agent.generate_credential_offer(
                        aip, None, bob_agent.cred_def_id, exchange_tracing
                    )
                    await bob_agent.agent.admin_POST(
                        "/issue-credential/send-offer", offer_request
                    )

                elif aip == 20:
                    if cred_type == CRED_FORMAT_INDY:
                        offer_request = bob_agent.agent.generate_credential_offer(
                            aip,
                            cred_type,
                            None,
                            exchange_tracing,
                        )

                    elif cred_type == CRED_FORMAT_JSON_LD:
                        offer_request = bob_agent.agent.generate_credential_offer(
                            aip,
                            cred_type,
                            None,
                            exchange_tracing,
                        )

                    else:
                        raise Exception(
                            f"Error invalid credential type: {cred_type}"
                        )

                    await bob_agent.agent.admin_POST(
                        "/issue-credential-2.0/send-offer", offer_request
                    )

                else:
                    raise Exception(f"Error invalid AIP level: {aip}")

            elif option == "3":
                msg = await prompt("Enter message: (ex: Hi Alice or Hi Faber or Faber, do ZKP) ")

                URL="http://"+DEFAULT_EXTERNAL_HOST+":8071/connections"
                r=requests.get(URL)
                resp=json.loads(r.text)
                resp2=list(resp['results'])
                issuer_connection_id=''
                connectee_connection_id=''
                cred_ex_id=""
                for i in resp2:
                    if i['their_label'] == "faber.agent":
                       issuer_connection_id = i['connection_id']
                    if i['their_label'] == "alice.agent":
                       connectee_connection_id = i['connection_id']
                
                if "Alice" in msg:
                   connectionid=connectee_connection_id
                elif "Faber" in msg:
                   connectionid=issuer_connection_id
                else:
                   connectionid=bob_agent.agent.connection_id          

                if msg:
                    await bob_agent.agent.admin_POST(
                        f"/connections/{connectionid}/send-message",
                        {"content": msg},
                    )

            elif option == "4":
                # handle new invitation
                log_status("Input new invitation details")
                await input_invitation(bob_agent)

            elif option == "5":
                log_msg(
                    "Creating a new invitation, please receive "
                    "and accept this invitation using X agent"
                )
                await bob_agent.generate_invitation(display_qr=True, wait=True)

            elif option == "6a":
                # Check if credential is revoked
                URL="http://"+DEFAULT_EXTERNAL_HOST+":8031/credentials"
                r=requests.get(URL)
                response_dict=json.loads(r.text)
                credential_id=response_dict['results'][0]['referent'] 
                URL="http://"+DEFAULT_EXTERNAL_HOST+":8031/credential/revoked/"+credential_id
                r=requests.get(URL)
                log_msg("URL: ",URL)
                log_msg(r)
                log_msg(r.text)
                response_dict=json.loads(r.text)
                revoked=response_dict['revoked']
                log_msg("Credential: ",credential_id," is revoked: ",revoked)
                if(not revoked):
                  msg = "ZKP"
                  if msg:
                     await bob_agent.agent.admin_POST(
                        f"/connections/{bob_agent.agent.connection_id}/send-message",
                        {"content": msg},
                     )
                else:
                    log_msg("Credential proof cannot be performed, credential revoked")

            elif option == "6b": 
                # handle hyperledger fabric
                URL="http://"+DEFAULT_EXTERNAL_HOST+":8031/credentials"
                r=requests.get(URL)
                response_dict=json.loads(r.text)
                #log_msg("bob_agent.agent.proved=",bob_agent.agent.proved) # HERE, COME HERE
                if(bob_agent.agent.proved):
                #if(len(response_dict['results'])!=0):
                   bob_credential=response_dict['results'][0]
                   serviceurl= bob_credential['attrs']['serviceurl']
                   accesstoken=bob_credential['attrs']['accesstoken']
                   customerid=bob_credential['attrs']['customerid'] 
                   operator=bob_credential['attrs']['operator']        

                   #url = "http://"+serviceurl+"/r,asset1"
                   url = "http://"+serviceurl

                   headers = CaseInsensitiveDict()
                   headers["Accept"] = "application/json"
                   headers["Authorization"] = "Bearer "+accesstoken

                   option = input('Select option: 1-list your tokens, 2-transfer token, 3-Order to charge token, 4-Transfer back from charge, 5-quit: ')
                   if option=="1":
                      url=url+"/ro,"+customerid
                      resp = requests.get(url, headers=headers)
                      #log_msg("url: ",url)
                      log_msg(resp.text)
                      #input_dict=json.loads(resp.text)
                      #log_msg(input_dict)
                      #x=list(filter(lambda x:x["Owner"]==customerid,input_dict))
                      #log_msg(x)

                   elif option=="2":
                      asset=input('Type your asset (e.g. asset1): ')
                      towhom=input('Type to whom you want to transfer your asset (e.g. Tom_id)')
                      url=url+"/to,"+asset+","+towhom+","+customerid
                      resp = requests.get(url, headers=headers)
                      log_msg(resp.text)
                      text="token "+asset+" has successfully transferred to "+towhom
                      log_msg(text)
                   elif option=="3":
                      asset=input('Type your asset (e.g. asset1): ')
                      url=url+"/tp,"+asset+","+customerid
                      resp = requests.get(url, headers=headers)
                      log_msg(resp.text)
                      text="token "+asset+" has successfully sent to charge for "+customerid
                      log_msg(text)
                      answer="False"
                      if "True" in resp.text:
                         answer="True"
                         log_msg(answer)
                   elif option=="4":
                      asset=input('Type your asset (e.g. asset1): ')
                      url=url+"/tb,"+asset+","+customerid
                      resp = requests.get(url, headers=headers)
                      log_msg(resp.text)
                      text="token "+asset+" has successfully received from charge for "+customerid
                      log_msg(text)
                      answer="False"
                      if "True" in resp.text:
                         answer="True"
                         log_msg(answer)
                   elif option=="5":
                      log_msg("quitting...")
                   else:
                      log_msg("wrong option!")
                else:
                   log_msg("credential not verified! (credential not proved or no credential)")
                bob_agent.agent.proved=False

        if bob_agent.show_timing:
            timing = await bob_agent.agent.fetch_timing()
            if timing:
                for line in bob_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await bob_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="bob", port=8070)
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
                "Bob remote debugging to "
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

    check_requires(args)

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
