# Dissertation: Network Analysis Based on Self-Sovereign Identity, An Approach on Energy Distributed Generation and Performance.

This github https://github.com/edbkei/dissertation intends to log input material obtained during design and test of SSI. The design is updated in the github https://github.com/edbkei/aries-cloudagent-python, that is forked from Hyperledger Aries Cloudagent https://github.com/aries-cloudagent-python. Both githubs give support to the dissertation writing. Dissertation is being prepared in overleaf.com and also stored in google drive, only available for master orientor professors.

## 1. General

## 2. Design

## 3. Test
### 3.1 Test Environment
#### 3.1.1 Nodes
VM1. IC (Instituto de Computação) Cloud - 2 vCPU - disk 79GB - OS Ubuntu 20.04.3 LTS - Codename Focal.
VM2. Google Cloud - 2 vCPU - disk 42GB - OS Ubuntu 20.04.3 LTS - Codename Focal. https://console.cloud.google.com/

#### 3.1.2 SW/APPS Install
1. Local Ledger VON-NETWORK. git clone https://github.com/bcgov/von-network.git
2. Aries Cloud Agent Python. git clone https://github.com/hyperledger/aries-cloudagent-python.git
3. Docker v2.2.2. Install instruction: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04-pt
4. Docker-compose v2.2.2. Install Instruction: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04-pt
5. Python v3.8. Install instruction: https://python.org.br/instalacao-linux/
6. DIF DID Universal Registrar. Install instruction: https://github.com/decentralized-identity/universal-registrar/blob/main/README.md
7. DIF DID Universal Resolver: Install instruction: https://github.com/decentralized-identity/universal-resolver
8. npm v8.3.0 and node v10.19.0. Install instruction for Nodejs: https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-ubuntu-20-04-pt
9. GHDID. Install instruction: https://github-did.com/
10. Hyperledger Fabric v1.4.7. Install Instruction: https://medium.com/coinmonks/install-and-configure-hyperledger-fabric-v1-4-on-ubuntu-18-04-3-lts-2ccbc7176887
11. Caliper v0.4.2 for measuring Hyperledger Fabric performance (TPS and Latency). Install instruction: https://hyperledger.github.io/caliper/v0.4.2/installing-caliper/


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
cd ~/aries-cloudagent-python/demo\
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo faber\
... to start faber agent with public ledger.\
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo alice\
... to start alice agent with public ledger.

#### 3.2.4 Perfomance
cd ~/aries-cloudagent-python/demo\
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance --count [count] --threads [threads]\
... to start performance agent with public ledger.

[count] = number of credentials being exchanged,\
[threads] = number of concurrent process.

Note 1: latency = average of credentials per second. See: https://stackoverflow.com/questions/54067812/the-way-to-count-tps-in-jmeter

Note 2: TPS = threads / latency. See: https://stackoverflow.com/questions/54067812/the-way-to-count-tps-in-jmeter

### 3.3 Basic Commands for setting up Hyperledger Fabric environment

#### 3.3.1 Environment 
Install at ~/go/src/github.com/youruser/fabric-samples

pip install Naked # http://sweetme.at/2014/02/17/a-simple-approach-to-execute-a-node.js-script-from-python/
  
#### 3.3.2 Hyperledger Fabric - Basic Token Transfer
Based on: https://hyperledger-fabric.readthedocs.io/en/release-2.2/write_first_app.html and https://hyperledger-fabric.readthedocs.io/en/latest/install.html

command line: node tokenapp.js arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8  
  
folder: ~/fabric-samples/asset-transfer-basic/application-javascript
 
|arg1     |arg2/5   |arg3/6              |arg4/7            | Description                                                          |
|---------|--------------|------------------|----------------|----------------------------------------------------------------------|
|init     |              |                  |                | Provide initial list of tokens in the ledger                         |
| all     |              |                  |                | List of tokens from ledger.                                          |
| read    | token      |                  |                | List specific asset token.                                           |
| create  | token      | InstallationID |EnergyKWH     | Create one asset. Token ID, installation ID, energy (KWH)            |
|         | Ts         |Owner            |AppraisedValue| Timestamp, Owner, Appraised value.                                   | 
| delete  | token      |                  |                | Delete asset token.                                                  | 
| transfer| token      | to another owner |                | Transfer token <asset> to another owner.                             | 
| exists  | token      |                  |                | Check if <token> exists                                              |
| update  | token      | InstallationID |EnergyKWH     | Update asset token. Token ID, installation ID, energy (KWH)          |
|         | Ts         | Owner          |AppraisedValue| Timestamp, Owner, Appraised value                                    |

             
 Examples:         
   
 | Command examples                                                        |Results                            |Fabric Interface|
 |-------------------------------------------------------------------------|-----------------------------------------|----------|
 | CRUD group:                                                             |                                         |          |
 |node tokenapp.js create assetx 123123123 10 2021-01-01T14:16:17 Tom 1300 |assetx token with its attributes, created.|createAssets|
 |node tokenapp.js read assetx                                             |assetx token attributes, read.           |ReadAsset|
 |node tokenapp.js update assetx 123123123 10 2021-01-01T14:16:17 Tom 1300 |assetx token attributes, updated.        |UpdateAsset|
 |node tokenapp.js delete assetx                                           |assetx token, deleted.                   |DeleteAsset|
 |Administrative group:                                                    |                                  |           |   
 |node tokenapp.js all                                                     |all tokens, listed.                      |GetAllAssets|
 |node tokenapp.js exists assetx                                           |True/False. About token assetx existance.|AssetExists|
 |node tokenapp.js init                                              |Initiate Ledger with a predefined list of tokens.|InitLedger |
 |node tokenapp.js transfer assetx OwnerB                            |assetx token is transferred from OwnerA to OwnerB|TransferAsset|
 
 IMPORTANT:                                                                                                                           
 A. First command of token application is: node tokenapp.js init. Read Preconditions in item B. 
  
 B. Preconditions: According to instruction: https://hyperledger-fabric.readthedocs.io/en/release-2.2/write_first_app.html and https://hyperledger-fabric.readthedocs.io/en/latest/install.html
  
    Issue commands as follow:                                                        
  
                             cd ~fabric-samples/test-network    
  
                             ./network.sh down     
  
                             docker ps -a    
  
                             ./network.sh up createChannel -c mychannel -ca    
  
                             make sure that tokenapp.js (in this github project) is at ~asset-transfer-basic/application-javascript
  
                             ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
  
  
    In another terminal do:        
  
                             cd ~asset-transfer-basic/application-javascript  
  
                             npm install  

                             node tokenapp.js arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8 
  
                             Note 1: In case the command fails, it may be necessary to delete folder wallet or restart from scratch (https://github.com/hyperledger/fabric-samples).
  
 C. To shutdown token application, do:              
  
                             cd ~fabric-samples/test-network  
  
                             ./network.sh down       
  
                             docker ps -a                                                                                         


#### 3.3.2 Hyperledger Caliper
Based on: https://hyperledger.github.io/caliper/v0.4.2/fabric-tutorial/tutorials-fabric-existing/
         
          https://hyperledger.github.io/caliper/v0.2/architecture/
  
          https://hyperledger.github.io/caliper-benchmarks/fabric/performance/2.1.0/nodeContract/nodeSDK/submit/delete-asset/

Note: Suppose that hyperledger caliper is installed under folder ../projects. The original folder is let at ../projects/caliper-workspace and working folder is let at ../projects/caliper-workspace2, whose design base is caliper-workspace.
  
From terminal 1: (there will be 2 for admin purpose)

Step 1: \
cd\
cd ~/projects/fabric-samples/test-network\
./network.sh up createChannel\
./network.sh deployCC -ccn basic -ccl javascript
  
From terminal 2:  
  
Step 2: \
cd\
cd ~projects/caliper-workspace2\
nano benchmarks/myAssetmark.yaml # update input data\
npx caliper launch manager --caliper-workspace ./ --caliper-networkconfig networks/networkConfig.yaml --caliper-benchconfig benchmarks/myAssetBenchmark.yaml --caliper-flow-only-test --caliper-fabric-gateway-enabled


Result:


| Name      | Succ | Fail | Send Rate (TPS) | Max Latency (s) | Min Latency (s) | Avg Latency (s) | Throughput (TPS) |
|-----------|------|------|-----------------|-----------------|-----------------|-----------------|------------------|
| readAsset | 3202 | 0    | 108.2           | 0.09            | 0.01            | 0.02            | 108.1            |

From terminal 1:
  
Step 3: Shutdown\
./network.sh down\
docker ps -a

Result: No docker containers.
  


## 4. Conclusion
