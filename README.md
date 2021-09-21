# Dissertation: Network Analysis Based on Self-Sovereign Identity, An Approach on Energy Distributed Generation and Performance.

This github https://github.com/edbkei/dissertation intends to log input material obtained during design and test of SSI. The design is updated in the github https://github.com/edbkei/aries-cloudagent-python, that is forked from Hyperledger Aries Cloudagent https://github.com/aries-cloudagent-python. Both githubs give support to the dissertation writing. Dissertation is being prepared in overleaf.com and also stored in google drive, only available for master orientor professors.

## 1. General

## 2. Design

## 3. Test
### 3.1 Test Environment

### 3.2 Basic Commands for setting up environment

#### 3.2.1 Docker commands

**Discovering IP addresses used in docker agents:** \
docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)

**OUTPUT (Example):** \
/alice - 172.17.0.2 \
/faber - 172.17.0.3

**Tcpdump:**\
Taking into account that current directory has tcpdump directory, and output will be done in tcpdump.pcap file.\
docker run --rm --net=host -v $PWD/tcpdump:/tcpdump kaazing/tcpdump
...\
Got n ... will appear, that means that tcpdump is listening packets.\
Ctrl+C ... to break tcpdump.

#### 3.2.2 Using Local Ledger
cd\
cd von-network\
./manage build     ... to build docker local network for the first time\
./manage up/start  ... to activate local ledger with 4 nodes.\
./manage down/stop ... to deactivate local ledger with 4 nodes.\

cd\
cd aries-cloudagent-python/demo\
./run_demo faber/alice/bob/acme  ... to activate agent faber or alice or bob or acme

OUTPUT (Example of Faber agent, interactive options):

<!-- TABLE_GENERATE_START -->
Faber      |                                               \
Faber      | ::::::::::::::::::::::::::::::::::::::::::::::\
Faber      | :: faber.agent                              ::\
Faber      | ::                                          ::\
Faber      | ::                                          ::\
Faber      | :: Inbound Transports:                      ::\
Faber      | ::                                          ::\
Faber      | ::   - http://0.0.0.0:8020                  ::\
Faber      | ::                                          ::\
Faber      | :: Outbound Transports:                     ::\
Faber      | ::                                          ::\
Faber      | ::   - http                                 ::\
Faber      | ::   - https                                ::\
Faber      | ::                                          ::\
Faber      | :: Public DID Information:                  ::\
Faber      | ::                                          ::\
Faber      | ::   - DID: PJohU8BPNkWqWAipipmVwU          ::\
Faber      | ::                                          ::\
Faber      | :: Administration API:                      ::\
Faber      | ::                                          ::\
Faber      | ::   - http://0.0.0.0:8021                  ::\
Faber      | ::                                          ::\
Faber      | ::                               ver: 0.6.0 ::\
Faber      | ::::::::::::::::::::::::::::::::::::::::::::::\
Faber      |\
Faber      | Listening...\
Faber      |\
Startup duration: 11.58s\
Admin URL is at: http://192.168.65.3:8021

Endpoint URL is at: http://192.168.65.3:8020

#3/4 Create a new schema/cred def on the ledger\
Schema:\
  {\
    "sent": {\
      "schema_id": "PJohU8BPNkWqWAipipmVwU:2:degree schema:71.54.57",\
      "schema": {\
        "ver": "1.0",\
        "id": "PJohU8BPNkWqWAipipmVwU:2:degree schema:71.54.57",\
        "name": "degree schema",\
        "version": "71.54.57",\
        "attrNames": [\
          "date",\
          "degree",\
          "age",\
          "timestamp",\
          "name"\
        ],\
        "seqNo": 98340\
      }\
    }\
  }

Schema ID: PJohU8BPNkWqWAipipmVwU:2:degree schema:71.54.57\
Cred def ID: PJohU8BPNkWqWAipipmVwU:3:CL:98340:faber.agent.degree_schema\
Publish schema/cred def duration: 15.51s

#7 Create a connection to alice and print out the invite details\
Generate invitation duration: 0.09s\
Use the following JSON to accept the invite from another demo agent. Or use the QR code to connect from a mobile agent.\
Invitation Data: (copy all {...} as invitation data for agents)
```diff
- {@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/connections/1.0/invitation", "@id": "716c58e9-80ad-4bf2-898e-6ad09240d4ae", "recipientKeys": ["BMaVNzXx972Y8kkxzmEgDqLDe9MS3qmGMDzBctHXui5E"], "serviceEndpoint": "http://192.168.65.3:8020", "label": "faber.agent"})
```

█▀▀▀▀▀▀▀█▀▀▀▀█▀▀██▀██▀▀▀▀█▀█▀██▀█████▀███▀███▀██▀▀▀▀█▀▀▀███▀███▀███████▀▀▀▀▀▀▀█
█ █▀▀▀█ ███▀█▀█▀▄▄ █▀ ▀▀█▄▀█ ▀█▀▀ █  ▀▄▄ ▄██ ▀▀ ▄▀▀▄█▀▀█▀▄█████▄█  ▄█ █ █▀▀▀█ █
█ █   █ █ ▄█▄   ▀█▀▄█ █▄ ▀  ▀ ▄▀██▄▀  ▀█▄▀█▀▀▄   ▀▀▀▄▄█ ▀█▀▄▀ ▄ ▄▀▄▀▀ █ █   █ █
█ ▀▀▀▀▀ █ ▄▀▄ █▀▄▀█ █▀▄▀█ █▀█ █▀▄▀█ █ █▀▄▀█▀█▀█ █▀█ ▄ █▀▄ ▄▀▄ █ █ ▄ █▀█ ▀▀▀▀▀ █
█▀███▀█▀▀ ▄▄█▄▄▀▄  ▄█▄ ▄  ▀▀▀ ▄▄▀▄█▀█ █▄▄▀▀▀██▄ ▀▀▀ █▄▄▄▄▀    ▀▀ ▄▀▀▄ ▀▀▀▀▀██▀█
█    █ ▀█▄ ▄▀ █▀ ▀ ▄▄▀ ▀ ▀ ▄  ▀▀ █   ▀ ▀▀▄█▀ ▀▄  ▄▀█  ██▄█▄ ▄█ ██▄▄▄▀ ▀   ▄▄▀ █
█▄▄▄▄▀█▀█▀▀▄█▄ ▀ ▄  ▀█▀█ █  ▀▀ ▄▀  ▀█ █▄█▄ █▀▄  █▄▄██ █  █ █▀█▀    ▄█▀ ▀ ▄▀▄███
█▀▀ ▀█▀▀█▀  ▀▀███ ▄██▀  ▄█▀▄  ██▄█▀▄██ ██ ▀▀ █▄ █▄█   █▄▀▄█▀ ▄▀█▀▀▄▄▀█ ▀█ ▄▀▀ █
█ ██▄██▀ ▄▀█▀█▀▀ ▄▄▄  ▀▀▀▄▀ ▄ █▄▀  ▀███▀██ ▄▀ ▄█▀█▀▀█  ▄ █▄▀██ █ █▄▀█▀▀▀▄██▄▄██
██▄ █▄█▀  █▄ ▀▀  █▀▄ ▀▀▄  █▀█▀ █▄▀▀█ ▄   █▀▀█▀▀ █▄▀▄████▀▄█  █▀▄▄ ▀██ ▀▄▄▄█▄▀▄█
█   ███▀ █▀ █▄▀▄██▄ █ ▄▀█▄▄█ █   ███▄▄ ███ ▄▀ ▄█  █▄▀▄   █▀▄█▀▀▄▀ █ █▀ ▄ ▄█▄  █
█ ▀▄   ▀▀ █▄▄▄  ▀█▄ ▄ ▄▀ █ ▀▄▀▀  ▄▀█▀▄▄ ▄▀▀ ▄▀▄  ▄ ▄█▄█▄███▀▀█▀▄▄█▄▀  █▀▀ █▄  █
█▀ ▄▄ ▀▀ ▀    █▀█▀▄▄ █▄▀    ▀ ▀▀ ▀▄█▄▄▀▀▄███▀▄▀ ▀▀  █▄██▄▀█▄▀█▀   ▀ ▀ ▀▀   █ ██
█▄▀▄█ █▀█ ▀▄▀▀█▄▀█▄ ▀▀ █  █▀█ █▄█▄█▀▀▀ █▀ █   ▀ █▀█   ██▄▀▄▀▀█▄█ ███  █▀█  ▄ ▄█
█  █▄ ▀▀▀ ▀▀  ▄ ▀▀▀ ▀▄ █▄ ▀▀▀ ▀█▀  ▀█ ▀ ▄▀▀  ▄▄ ▀▀▀ ▄▄█▀▀█▄▀▀▀█▄█ █▄▀ ▀▀▀ ▀▄███
█▀▄▀█▄█▀▀▀▄▀█▀▀▀█▄▄▄▀▀▄ █   ▄▀█ ▀ █▄██  ▀▀█ █▀█▄▄█▀▄ █▄▄██▄▀ █▀▀█ ▄▄▄▀▀▀█▄ ▄▀▄█
█▀█▄█▄ ▀▀▀▄  ▄███ ▄█▄ ▀▄█▄█▄██▄▄ ▄ ▄█▀ █▄█ ▀  ▄▄▀▄▄█▄ ▄  █▄█▀▀ ▀▀▄▄ ▀▀▄▀███  ▄█
██▀▀▄ █▀▄  █   █ ▄█▀▀▀▄▄  ▀█▄▄████▀█ ▄ ▀███▄▄▀ ▄   █▀█▄▄ ▄▀ ▀▀ █▀▄▄█▄▄█  ▄ ▀▀▀█
███▄▄▀ ▀▀▄█▄█▀███▄▀▄▀█▀█▄█ ▀▀▀ ▀▀ ▀▄█ █▄▄█▄█  ▄█▀█ ██ █▄ ▄▄▀▀▀▀▀█ ▀▀ ▄▄▀█▄██▄▄█
█▄▀▄▄█▀▀▄▀▀▀▀▀██▄▄▀▄▀ █▀▄ ▄▄▀ █▄▀ ████  ▄▀█▀ ██ ▄█▀ ▄▀▄▄▄ ▀▀▄▄▄█ ▄▄▄█▀ ▀▄▄█ ▀ █
█▄ █▄▀▀▀  ▄█▀  ▄██▄ ▀ █ ▀ ▄█▄███  ▀ █ █▀█▄ █▀▄▄ ▄▄ ▀▀▄▄ ▀█▀█▀█▄ ▀▄▄▄▀█ ▀▀ ▀█▄ █
█▄█ ██▄▀ ▀▄▄█▄█▀ ▄▄█▀▄▄ █▄ ▄ ▄█▀█▀██▀▀ ▄ ▀█▀▄  ▄██▄█▀█▀█▄ █ ▀▀▀█▀█▄▄ █▀▄█▄▄ ▀ █
█ ▄▄▀▀▄▀▀█ ▀▀▄█▀▀█▄███▀▀█ ▄▄███▄▀▄  ▄▄▀██▀▄▀ █▄█▄▀██▄ ▀  ▀█ ▄ █▀▀▄▀▀█▄▄▀█▀█▄▀▄█
█▀█▀▄ ▀▀  ▀▄▀▀▄ ▀▀█▀  █▀▀▀▀▀ ▀ ▄█▀███▄▄ ███▀ ▄▄  ▀   ▄▀▄ ▀█ ▀▀ ██▄██▄▀▀▀▀ █   █
█▄▀▄▀ █▀█ ▄▄▄█▀█▀█▄▄█▀█▀▄ █▀█  █ ▄ ▄█▀▄▀█ ▄▄ ▀▄ █▀█ ▀▄██▄█▄ ▄█▀ ▄ ▄█  █▀█ ▀▄█ █
██▀▄▀ ▀▀▀ █▀▄▄▄  █ ▀▄█▄ ▄ ▀▀▀ ▄▀  █▀█▄▄▀▀ ▀ █▄█ ▀▀▀  ▀███▀▄▀▀  ██▀▄██ ▀▀▀  ▀▀ █
█ █▄▀█ ▀   ▄  ▄▀█▀▀█ ▄██▀ ▀▄▄ ▄▄  ▀██ ▀▄█▀█▀ ▄█ ██▄ ▀ ▄▀▀█▄ ▀█▄▀ ▄  ▄▀▄▀ ▄▀▄ ▄█
█▀▀█▄▄█▀█▄▄ █▄  █▀▀█▄██▀██▀ █▄█▀ ▄▀█   ██▀█▀ ▄ ▀ ▄█▄▀▄▄▄ ▄▄ ▄ ███▄█▄█▄▀▄▀▀▄▀ ▄█
█  ▀▄▀ ▀  ▄ ▄ ▀▄ █▀▀  ▄▀ ▄▄ ▄▄ ▄▀ ▄▀▄  ▀██▄▄ ▄█ █▀▀  ▄██▄▀ ▀██  ▄ ▀██ ▄▀▀█▀▄▄▀█
█▀ ▄▄▄ ▀█▄▄  ▀▀█ █▀█  ▄█▄███▄ █▀██▀▄▄ ▄ █▀█ ▀█▄█▄ ▄▀ ███ ██ ▀▄ ▄▀█  ▀  ██ ▀  ▄█
██ ▄█▄▀▀▄▀▄█▀ ▄ ▄█   █▄█▀ █▄  █▀▀▄ ██   ▄█ █▀▄▀▄██▄▀  ▄▀▄▀▀▄▀▀▀▄▀▄█▀  █▄███▀  █
█ ▀▄█▀▀▀▀ █ ▀▀█▄▄ █▄ ▄ █ █ ▀█▀  █ ██   █▄ ▀ ▄▄▄  ▄▄█▄███ ▀▄▀█ ▀▄▀ ▄▀▀ █ █▄▄█ ▄█
█▀█ ▀▀▀▀▄ ▀  █▀▄▄█ ▀█▄▀▄█▄█▄▀▄▀▄██▄█▄ █ ▄▀▀  ▄ ███▀ █▄ ▄▄▀▄ ▀▀▄▄▀ ▄ ███▀ ▄▄████
█▄ ▄▄▀ ▀█  ▀▄▀▄ ▀▀██▀███▀  ▄█▀▀█ ▀▀█   ▀▄ ▀ █▄▄▄█▀▄█▄█▄█▄▄▄▀▀██ ▀█ ██  ▀▀ ▀▄▀▄█
██▀▀▀ █▀▀▀ ▄▀▀ █▀▀     ▄▄▀▀▀  ▀ ▀ ▄▄█ █ ███▀ ▄▀ ▀▀ ▀ █ ▄▄█  ▀█ █▀▄█▄▀▀    ███ █
█▀▀▀▀▀▀▀█   ▄█▀▀ ▀ █    █ █▀█  █▀█▀▄█▄▄▀ ▄▀  ▄█ █▀█  ▀▄▄▀ ▄▀▀▀   ▄ ▄  █▀█  ▀▀ █
█ █▀▀▀█ █▀ ▄█▀▄███▄▄ ▀▀█▀ ▀▀▀ ▄   ▄▀ █ ▀███▄▀   ▀▀▀  █▄██▀▀▀▀▀██▀ ▄▄█ ▀▀▀ █▄█▀█
█ █   █ ████▄██▄█▄▀ ▀█▄▄██  ▄ ▀▀▀▄▀▄█▀ ██  █▀ ██ █▄ ▄ ▄▄   ██ ▀█  ███▀▀▀ █ ▄▀▀█
█ ▀▀▀▀▀ █▀▄█▀▄█▀█▀▄  █▄█▄▀█▀█▀▄▀▀ ▀█▄▄  ▄▀█ ▀ ██ ▀▄▄▀▄ ▄▄▀▄▄▄█  █▄▀▀▀ ▄▄▄▄██ ▄█
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
Waiting for connection...\
http://dev.greenlight.bcovrin.vonx.ioFaber      | Connected\
Faber      | Received message: Hey Faber, send me a credential!\
    (1) Issue Credential\
    (2) Send Proof Request\
    (3) Send Message\
    (4) Create New Invitation\
    (T) Toggle tracing on credential/proof exchange\
    (X) Exit?\
[1/2/3/4/T/X] 1

#13 Issue credential offer to X\
Faber      | Credential: state = offer-sent, cred_ex_id = b920f9cb-830e-4a4c-a1e6-038cee028546\
Faber      | Credential: state = request-received, cred_ex_id = b920f9cb-830e-4a4c-a1e6-038cee028546\

#17 Issue credential to X\
Faber      | Credential: state = credential-issued, cred_ex_id = b920f9cb-830e-4a4c-a1e6-038cee028546\
Faber      | Credential: state = done, cred_ex_id = b920f9cb-830e-4a4c-a1e6-038cee028546\
    (1) Issue Credential\
    (2) Send Proof Request\
    (3) Send Message\
    (4) Create New Invitation\
    (T) Toggle tracing on credential/proof exchange\
    (X) Exit?\
[1/2/3/4/T/X] 2

#20 Request proof of degree from X\
Faber      | Presentation: state = request-sent, pres_ex_id = a0a3a62f-4b38-4cac-a7e5-3668f8829053\
Faber      | Presentation: state = presentation-received, pres_ex_id = a0a3a62f-4b38-4cac-a7e5-3668f8829053

#27 Process the proof provided by X

#28 Check if proof is valid\
Faber      | Presentation: state = done, pres_ex_id = a0a3a62f-4b38-4cac-a7e5-3668f8829053\
Faber      | Proof = true\
    (1) Issue Credential\
    (2) Send Proof Request\
    (3) Send Message\
    (4) Create New Invitation\
    (T) Toggle tracing on credential/proof exchange\
    (X) Exit?\
[1/2/3/4/T/X] x\
Shutting down agent ...\
Faber      |\
Faber      | Shutting down\
Faber      | Exited with return code 0\
ubu20w@DESKTOP-CT0HBV1:~/aries-cloudagent-python/demo$


#### 3.2.3 Using Public Ledger
cd\
cd ~aries-cloudagent-python/demo\
LEDGER_URL=http://http://dev.greenlight.bcovrin.vonx.io ./run_demo faber ... to start faber agent with public ledger.\
LEDGER_URL=http://http://dev.greenlight.bcovrin.vonx.io ./run_demo alice ... to start alice agent with public ledger.

#### 3.2.3 Perfomance
cd\
cd ~aries-cloudagent-python/demo\
LEDGER_URL=http://http://dev.greenlight.bcovrin.vonx.io ./run_demo performance --count [count] --threads [threads] ... to start performance agent with public ledger.

[count] = number of credentials being exchanged,\
[threads] = number of concurrent process.

Note 1: latency = average of credentials per second. See: https://stackoverflow.com/questions/54067812/the-way-to-count-tps-in-jmeter

Note 2: TPS = threads / latency. See: https://stackoverflow.com/questions/54067812/the-way-to-count-tps-in-jmeter

## 4. Conclusion
