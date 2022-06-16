# Dissertation: Accessibility by means of Self-Sovereign Identity to the Energy Tokens received from Distributed Generation, An Approach with Multiple Blockchain Platform for treatment of Non Fungible Tokens Data.

This github https://github.com/edbkei/dissertation intends to log input material obtained during design and test of SSI. The design is updated in the github https://github.com/edbkei/aries-cloudagent-python, that is forked from Hyperledger Aries Cloudagent https://github.com/aries-cloudagent-python. Both githubs give support to the dissertation writing. Dissertation is being prepared in overleaf.com and also stored in google drive, only available for master orientor professors.

# 1. General

# 2. Design
## 2.1 Web Design
As the execution of hyperledger Aries agent is based docker container, i.e. it is like a new virtual machine running ubuntu on a "host" virtual machine, and the necessary line command for execution of Hyperledger Fabric that is in "host" virtual machine requires
a web design. Flask library is installed (pip install Flask) for running on Python application. In this way, Flask apps can run curl command to make http request to execute fabric command on "host" virtual machine.

get server.py at https://github.com/edbkei/dissertation/tree/main/Flask/ledgerserver
For execution of Flask apps:\
export FLASK_RUN_PORT=port (e.g. 8080) \
export FLASK_APP=server.py \
flask run --host=0.0.0.0

Note: This is replaced by https://github.com/edbkei/dissertation/blob/main/TestEnvironment/VM1_Faber/startweb.sh

apps.py contains execution command module of Hyperledger Fabric. Binding to 0.0.0.0 is necessary to external IP be visible. Command netstat -antp or ss -lntp can be used to check ports are up and running.

# 3. Test
## 3.1 Test Environment
### 3.1.1 Nodes
VM1. IC (Instituto de Computação) Cloud - 2 vCPU - disk 79GB - OS Ubuntu 20.04.3 LTS - Codename Focal.\
VM2. Google Cloud - 2 vCPU - disk 42GB - OS Ubuntu 20.04.3 LTS - Codename Focal. \
VM3. Google Cloud - 2 vCPU - disk 39GB - OS Ubuntu 20.04.3 LTS - Codename Focal.

VM Node configurations and scripts are stored at directory ../dissertation/tree/main/TestEnvironment, where there are subdirectories VM1_Faber, VM2_Alice, and VM3_Bob.
The most important is VM1_Faber that represents the Faber Energy Operator, and VM2_Alice is the energy prossumer, and VM3_Bob is the energy consumer. Each one has specific ways to perform tests. These are:

VM1_Faber has the following scripts:
* agent.py. Same as existing in Hyperledger Aries design base with only change in external IP address, and timer.
* agent_container.py. Same as agent.py.
* faber.py. Same as agent.py
* editcouchdb.sh. Used to change stateDatabase to LevelDB (default) or CouchDB (that is based on SQL).
* start2nodes.sh. Start Hyperledger Fabric with 2 nodes (default). It is used in performance test.
* start3nodes.sh. Start Hyperledger Fabric with 3 nodes. 3rd node is mounted with new cryptographic material (private key, certificates). It is used in performance test.
* startaries.sh. Start Hyperledger Aries agent Faber.
* startcaliper.sh.  Start Hyperledger Fabric performance test.
* startfabric.sh. Similar to start2nodes.sh, but with different wallet. It is used before running, startweb.sh.
* startweb.sh. Start AAA Web Service.
* stop2nodes.sh. Stop Hyperledger Fabric that uses 2 nodes.
* stop3nodes.sh. Stop Hyperledger Fabric that uses 3 nodes.
* stopfabric.sh. Same as stop2nodes.sh.

VM2_Alice has the following scripts:
* agent.py. Same as existing in Hyperledger Aries design base with only change in external IP address, and timer.
* agent_container.py. Same as agent.py
* alice.py. Same as agent.py
* startaries.sh. Start Hyperledger Aries agent Alice.

VM3_Bob has the following scripts:
* agent.py. Same as existing in Hyperledger Aries design base with only change in external IP address, and timer.
* agent_container.py. Same as agent.py
* bob.py. Same as agent Alice, change in the name convention to Bob.
* startaries.sh. Start Hyperledger Aries agent Bob
* startperformance.sh. Run performance.py with parameters threads and count.
* starttcpdump.sh. Run tcpdump to log traffic data.
* startariesrevoke.sh. Run hyperledger aries to register into ledger that supports revocation.

### 3.1.2 How to use scripts
#### 3.1.2.1 VM1_Faber
* To Start full Use Case

In terminal 1: ./startfabric.sh\
In terminal 2: ./startweb.sh\
In terminal 3: ./startaries.sh

* To Stop full Use Case

In terminal 3: X option in user UI.\
In terminal 2: CTRL+C\
In terminal 1: ./stopfabric.sh

* To start test performance with 2 nodes

In terminal 1: edit database LevelDB/couchDB: ./editcouchdb.sh \
In terminal 1: ./start2nodes.sh\
In terminal 2: ./startcaliper.sh\

* To stop test performance with 2 nodes

In terminal 2: ./stop2nodes.sh

* To start test performance with 3 nodes

In terminal 1: edit database LevelDB/couchDB: ./editcouchdb.sh \
In terminal 1: ./start3nodes.sh\
In terminal 2: ./startcaliper.sh\

* To stop test performance with 2 nodes

In terminal 2: ./stop3nodes.sh

#### 3.1.2.2 VM2_Alice
* To Start full Use Case

In terminal 1: If local ledger: \
               cd von-network\
               manage build\
               manage start \
               \
               If remote ledger: edit startaries.sh
               
In terminal 1: ./startaries.sh\

* To stop full Use Case

In terminal 1 Type option X in user UI.

Note 1: in VM2_Alice performance test only executed with 4 nodes for local ledger.

#### 3.1.2.3 VM3_Bob
* To Start full Use Case

In terminal 1: If local ledger: \
               cd von-network\
               manage build\
               manage start \
               \
               If remote ledger: edit startaries.sh
               
In terminal 1: ./startaries.sh\

Support revogation, in terminal 1: ./startariesrevoke.sh

* To stop full Use Case

In terminal 1 Type option X in user UI.

Note 1: in VM3_Bob performance test only executed with 7 nodes for local ledger.

* To run performance

In terminal 1: ./startperformance.sh

* To run tcpdump

In terminal 1: ./starttcpdump.sh



### 3.1.3 SW/APPS Install
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
12. Class: ChaincodeStub  : https://hyperledger.github.io/fabric-chaincode-node/release-2.2/api/fabric-shim.ChaincodeStub.html#getStateByRange__anchor
13. Attribute Based Access Control: https://github.com/hyperledger/fabric-samples/blob/main/asset-transfer-abac/README.md
14. Fabric Contract API: https://hyperledger-fabric.readthedocs.io/en/release-2.2/chaincode4ade.html#fabric-contract-api

Note: Specific authorization per user requires flexibility in the choice of ledger technology, for instance getQueryResult(query), that performs a rich query in ledger, only works with CouchDB, accordingly to reference [12].

## 3.2 Basic Commands for setting up environment

### 3.2.1 Docker commands

**Discovering IP addresses used in docker agents:** \
docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)

**OUTPUT (Example):** \
/alice - 172.17.0.2 \
/faber - 172.17.0.3

**Tcpdump:**\
Taking into account that current directory has tcpdump directory, and output will be done in tcpdump.pcap file.\
docker run --rm --net=host -v $PWD/tcpdump:/tcpdump kaazing/tcpdump\
Got n ... will appear, that means that tcpdump is listening packets.\
Ctrl+C ... to break tcpdump.

### 3.2.2 Using Local Ledger, using Hyperledger indy (von-network) for Hyperledger Aries agents
cd\
cd von-network\
./manage build     ... to build docker local network for the first time\
./manage up/start  ... to activate local ledger with 4 nodes (default).\
./manage down/stop ... to deactivate local ledger with 4 nodes (default).

Note: 4 nodes can be observed at http://xx.xx.xx.xx:9000, where is x..x is the IP of VM.

### 3.2.3 Hyperledger Indy using 7 nodes (the number of nodes must follow the rule: N=3n+1, where n is 1,2,3...)
Note 1: Follow instruction to add New Nodes in 
https://github.com/bcgov/von-network/blob/main/docs/AddNewNode.md

Afected files in von-network:\
~/von-network/docker-compose.yml. Add new ports for new nodes.\
~/von-network/scripts/start_nodes.sh. Assign ports to new nodes.\
~/von-network/bin/von_generate_transactions. Assign new ports for new nodes.

Note 2: 7 nodes can be observed at http://xx.xx.xx.xx:9000, where is x..x is the IP of VM, like figure below.

![Screenshot](https://github.com/edbkei/dissertation/blob/main/Images/7nodes.jpg)

Note 3: Make sure to allow ports 8050-8059 in firewall.

Note 4: Make sure that web (i.e. port 9000) will start only after all nodes are started. \
        Adjust if necessary the sleep time at ~/von-network/docker-compose.yml.
        
Note 5: There are others ways to add extra nodes onto default 4 nodes. INDY-SDK should be installed:
        https://github.com/hyperledger/indy-sdk. 
        Nevertheless, libraries (libindy, libnullpay, libvcx or indy-cli) installation is not stable depending on OS used. 
        So for, the usage of reference mentioned in Note 1 is what was possible to be worked out at writing this README.

### 3.2.4 Starting Hyperledger Aries Agents

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
![Screenshot](https://github.com/edbkei/dissertation/blob/main/Images/qrcode.JPG)

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


#### 3.2.5 Using Public Ledger
cd ~/aries-cloudagent-python/demo\
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo faber\
... to start faber agent with public ledger.\
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo alice\
... to start alice agent with public ledger.

Note: This is replaced by https://github.com/edbkei/dissertation/blob/main/TestEnvironment/VM1_Faber/startaries.sh, at VM1 to run agent Faber.
                          https://github.com/edbkei/dissertation/blob/main/TestEnvironment/VM2_Alice/startaries.sh, at VM2 to run agent Alice.
                          https://github.com/edbkei/dissertation/blob/main/TestEnvironment/VM3_Bob/startaries.sh, at VM3 to run agent Bob.

#### 3.2.6 Perfomance Hyperledger Aries
cd ~/aries-cloudagent-python/demo\
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance --count [count] --threads [threads]\
... to start performance agent with public ledger.

[count] = number of credentials being exchanged,\
[threads] = number of concurrent process.

Note 1: latency = average of credentials per second. See: https://stackoverflow.com/questions/54067812/the-way-to-count-tps-in-jmeter

Note 2: TPS = threads / latency. See: https://stackoverflow.com/questions/54067812/the-way-to-count-tps-in-jmeter

Note 3: Timer is always issue for different problems: Adjust as necessary the Parameter START_TIMEOUT at AGENT.PY, faber.detect_connection() and agent.update_creds() at PERFORMANCE.PY.\
        The fault: Exception: Error: 400: Credential definition xxxx is in wallet faber999 but not on ledger default can be solved at agent.update_creds()
        

### 3.3 Basic Commands for setting up Hyperledger Fabric environment

#### 3.3.1 Environment 
Install at ~/go/src/github.com/youruser/fabric-samples

pip install Naked # http://sweetme.at/2014/02/17/a-simple-approach-to-execute-a-node.js-script-from-python/
  
### 3.3.2 Hyperledger Fabric - Basic Token Transfer
Based on: https://hyperledger-fabric.readthedocs.io/en/release-2.2/write_first_app.html and https://hyperledger-fabric.readthedocs.io/en/latest/install.html

command line: node tokenapp.js arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8  
  
folder: ~/fabric-samples/asset-transfer-basic/application-javascript
 
|arg1     |arg2/5   |arg3/6              |arg4/7            | Description                                                          |
|---------|--------------|------------------|----------------|----------------------------------------------------------------------|
|init     |              |                  |                | Provide initial list of tokens in the ledger                         |
| all     |              |                  |                | List of tokens from ledger.                                          |
| read    | token      |                  |                | List specific asset token.                                           |
| create  | token      | FinalConsumer |EnergyKWH     | Create one asset. Token ID, FinalConsumer, energy (KWH)              |
|         | Status         |Owner            |AppraisedValue| Status, Owner, Appraised value.                                     | 
| delete  | token      |                  |                | Delete asset token.                                                  | 
| transfer| token      | to another owner |                | Transfer token <asset> to another owner.                             | 
| exists  | token      |                  |                | Check if <token> exists                                              |
| update  | token      | FinalConsumer |EnergyKWH     | Update asset token. Token ID, FinalConsumer, energy (KWH)           |
|         | Status         | Owner          |AppraisedValue| Status, Owner, Appraised value                                       |

             
 Examples:         
   
 | Command examples                                                        |Results                            |Fabric Interface|
 |-------------------------------------------------------------------------|-----------------------------------------|----------|
 | CRUD group:                                                             |                                         |          |
 |node tokenapp.js create assetx none 10 onchain Tom 1300                  |assetx token with its attributes, created.|createAssets|
 |node tokenapp.js read assetx                                             |assetx token attributes, read.           |ReadAsset|
 |node tokenapp.js update assetx none 10 onchain Tom 1300                  |assetx token attributes, updated.        |UpdateAsset|
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
  
                             cd fabric-samples/asset-transfer-basic/application-javascript\
                             *** following recommendation: it is under directory ~/go/src/github.com/user
  
                             rm -r wallet
  
                             cd ../../test-network    
  
                             ./network.sh down     
  
                             docker ps -a    
  
                             ./network.sh up createChannel -c mychannel -ca    

                             ./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript  
  
                             cd ../asset-transfer-basic/application-javascript  
  
                             npm install  
  
                             *** make sure that tokenapp.js (in this github project) is at ~asset-transfer-basic/application-javascript

                             node tokenapp.js arg1 arg2 arg3 arg4 arg5 arg6 arg7 arg8 
  
                             Note 1: In case the command fails, it may be necessary to delete folder wallet or restart from scratch (https://github.com/hyperledger/fabric-samples).
                             Note 2: This part is replaced by https://github.com/edbkei/dissertation/tree/main/TestEnvironment/VM1_Faber/startfabric.sh
  
 C. To shutdown token application, do:              
  
                             cd fabric-samples/test-network  
  
                             ./network.sh down       
  
                             docker ps -a   
  
                             Note: This part is replaced by https://github.com/edbkei/dissertation/blob/main/TestEnvironment/VM1_Faber/stopfabric.sh

D. Python scripts of Node.js scripts for operational tasks

The asset manager is composed by scripts: do.py, token_manager.py, tokenapp.js, any input file .txt (example is file1.txt).
do.py and token_manager.py are python scripts, and tokenapp.js is node.js script.
  
The files tokenapp.js and token_manager.py requires to be together at directory ~/go/src/github.com/user/fabric-samples
  /asset-transfer-basic/application-javascript/. The file do.py can be put in any place to execute. assetTransfer.js is
  part of chaincode (smart contract) asset-transfer-basic and is located at ~/go/src/github.com/user/fabric-samples
  /asset-transfer-basic/chaincode-javascript/lib/.
  
The executable file do.py has the following syntax: ./do.py arg1 arg2 arg3.
  
./do.py h. This command displays help with all parameter combinations.\
./do.py c arg2. This command (c)reates new asset containing in file pointed by arg2. It runs interface CreateAsset.\
./do.py r arg2. This command (r)eads the asset pointed by arg2. It runs interface ReadAsset.\
./do.py u arg2. This command (u)pdates the asset pointed by file in arg2. It runs interface UpdateAsset.\
./do.py d arg2. This command (d)eletes the asset pointed by arg2. It runs interface DeleteAsset.\
./do.py e arg2. This command checks if asset pointed by arg2 (e)xists. It runs interface AssetExists.\
./do.py a. This command reads all assets existing in the ledger. It runs interface GetAllAssets.\
./do.py t arg2 arg3. This command (t)ransfer asset pointed by arg2 to new owner pointed by arg3. It runs interface TransferAsset.
  
Note: the script do.py will be used to control asset in the ledger of hyperledger fabric, and its behaviour will be used by
  hyperledger aries agents to complete the business case.
  
  
### 3.3.3 Hyperledger Caliper
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
nano benchmarks/myAssetBenchmark.yaml # update input data\
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
  
## 3.4 Environment faults
Fault 1: [comm.tls] ClientHandshake -> ERRO 003 Client TLS handshake failed after 1.908956ms with error: EOF remoteaddress=127.0.0.1:7051
Error: error getting endorser client for channel: endorser client failed to connect to localhost:7051: failed to create new connection: context deadline exceeded
After 5 attempts, peer0.org1 has failed to join channel 'mychannel'\
Solution: Reinstall docker, acc to https://hyperledger-fabric.readthedocs.io/fa/latest/test_network.html
        
Fault 2: SSL_ERROR_SYSCALL openssl\
From VM_IC, when executing ./startaries.sh, error SSL_ERROR_SYSCALL is issued.\
Root cause: IC Cloud Datacenter policy establish MTU size to 1450 bytes, but interface docker0 shows that 1500 bytes is set in ifconfig.\
Final Solution:\
sudo nano /etc/docker/daemon.json\
{\
        "mtu": 1450\
}\
systemctl restart docker
        
Redo ./startaries.sh       
        
        

# 4. Conclusion
