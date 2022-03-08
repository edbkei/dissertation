import asyncio
import base64
import binascii
import json
import logging
import os
import sys
import requests
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


class AliceAgent(AriesAgent):
    def __init__(
        self,
        ident: str,
        http_port: int,
        admin_port: int,
        no_auto: bool = False,
        aip: int = 20,
        endorser_role: str = None,
        **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="Alice",
            no_auto=no_auto,
            seed=None,
            aip=aip,
            endorser_role=endorser_role,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}

    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()


async def input_invitation(agent_container):
    agent_container.agent._connection_ready = asyncio.Future()
    async for details in prompt_loop("Invite details: "):
        b64_invite = None
        try:
            url = urlparse(details) # print url
            print("url type: ",type(url))
            print("url: ",url)
            ip=get('https://api.ipify.org').text
            print("ip type:", type(ip))
            print("ip: ",ip)
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
                print("type(details):", type(details))
                print("details: ",details)
                break
            except json.JSONDecodeError as e:
                log_msg("Invalid invitation:", str(e))

    with log_timer("Connect duration:"):
        connection = await agent_container.input_invitation(details, wait=True)


async def main(args):
    alice_agent = await create_agent_with_args(args, ident="alice")

    try:
        log_status(
            "#7 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {alice_agent.wallet_type})"
                if alice_agent.wallet_type
                else ""
            )
        )
        agent = AliceAgent(
            "alice.agent",
            alice_agent.start_port,
            alice_agent.start_port + 1,
            genesis_data=alice_agent.genesis_txns,
            genesis_txn_list=alice_agent.genesis_txn_list,
            no_auto=alice_agent.no_auto,
            tails_server_base_url=alice_agent.tails_server_base_url,
            revocation=alice_agent.revocation,
            timing=alice_agent.show_timing,
            multitenant=alice_agent.multitenant,
            mediation=alice_agent.mediation,
            wallet_type=alice_agent.wallet_type,
            aip=alice_agent.aip,
            endorser_role=alice_agent.endorser_role,
        )

        await alice_agent.initialize(the_agent=agent)

        #log_status("#9 Input faber.py invitation details") -- here
        #await input_invitation(alice_agent)

        options = "    (3) Send Message\n" "    (4) Input New Invitation\n" "    (5) Create New Invitation\n" "    (6) Energy Token Management\n"
        if alice_agent.endorser_role and alice_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if alice_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
        options += "    (X) Exit?\n[3/4/5/6/{}X] ".format(
            "W/" if alice_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and alice_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await alice_agent.agent.admin_POST(
                    f"/transactions/{alice_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did, "endorser_name": "endorser"},
                )

            elif option in "wW" and alice_agent.multitenant:
                target_wallet_name = await prompt("Enter wallet name: ")
                include_subwallet_webhook = await prompt(
                    "(Y/N) Create sub-wallet webhook target: "
                )
                if include_subwallet_webhook.lower() == "y":
                    await alice_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        webhook_port=alice_agent.agent.get_new_webhook_port(),
                        mediator_agent=alice_agent.mediator_agent,
                    )
                else:
                    await alice_agent.agent.register_or_switch_wallet(
                        target_wallet_name,
                        mediator_agent=alice_agent.mediator_agent,
                    )

            elif option == "3":
                msg = await prompt("Enter message: ")
                if msg:
                    await alice_agent.agent.admin_POST(
                        f"/connections/{alice_agent.agent.connection_id}/send-message",
                        {"content": msg},
                    )

            elif option == "4":
                # handle new invitation
                log_status("Input new invitation details")
                await input_invitation(alice_agent)

            elif option == "5":
                log_msg(
                    "Creating a new invitation, please receive "
                    "and accept this invitation using X agent"
                )
                await alice_agent.generate_invitation(display_qr=True, wait=True)


            elif option == "6": 
                # handle hyperledger fabric
                #URL=DEFAULT_EXTERNAL_HOST+"/credentials"
                URL='http://104.198.179.213:8031/credentials'
                r=requests.get(URL)
                response_dict=json.loads(r.text)
                if(len(response_dict['results'])!=0):
                   alice_credential=response_dict['results'][0]
                   serviceurl= alice_credential['attrs']['serviceurl']
                   accesstoken=alice_credential['attrs']['accesstoken']
                   customerid=alice_credential['attrs']['customerid'] 
                   operator=alice_credential['attrs']['operator']          

                   #url = "http://"+serviceurl+"/r,asset1"
                   url = "http://"+serviceurl

                   headers = CaseInsensitiveDict()
                   headers["Accept"] = "application/json"
                   headers["Authorization"] = "Bearer "+accesstoken

                   option = input('Select option: 1-list your tokens, 2-transfer token, 3-Order to charge token, 4-quit: ')
                   if option=="1":
                      url=url+"/a"
                      resp = requests.get(url, headers=headers)
                      input_dict=json.loads(resp.text)
                      x=list(filter(lambda x:x["Owner"]==customerid,input_dict))
                      log_msg(x)

                   elif option=="2":
                      asset=input('Type your asset (e.g. asset1): ')
                      towhom=input('Type to whom you want to transfer your asset (e.g. Tom_id)')
                      url=url+"/t,"+asset+","+towhom
                      resp = requests.get(url, headers=headers)
                      log_msg(resp.text)
                      text="token "+asset+" has successfully transferred to "+towhom
                      log_msg(text)
                   elif option=="3":
                      asset=input('Type your asset (e.g. asset1): ')
                      url1=url+"/e,"+asset
                      resp = requests.get(url1, headers=headers)
                      if "True" in resp.text:
                         url2=url+"/r,"+asset
                         resp = requests.get(url2, headers=headers)
                         attributes=json.loads(resp.text)
                         appraisedValue=attributes['AppraisedValue']
                         energyKWH=attributes['EnergyKWH']
                         id=attributes['ID']
                         finalConsumer=attributes['Owner']
                         owner=operator
                         status="CHARGE"
                         docType=attributes['DocType']
                         updated=asset+","+finalConsumer+","+energyKWH+","+status+","+owner+","+appraisedValue+","+docType
                         url3=url+"/uu,"+updated
                         updating="token updated: "+updated
                         log_msg(updating)
                         resp = requests.get(url3, headers=headers)
                         answer="False"
                         if "True" in resp.text:
                            answer="True"
                         log_msg(answer)
                      else:
                         x="Token "+asset+" not exists!"
                         log_msg(x)
                   elif option=="4":
                      log_msg("quitting...")
                   else:
                      log_msg("wrong option!")
                else:
                   log_msg("credential not provided!")
           

        if alice_agent.show_timing:
            timing = await alice_agent.agent.fetch_timing()
            if timing:
                for line in alice_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await alice_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="alice", port=8030)
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
                "Alice remote debugging to "
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
