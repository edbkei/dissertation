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

#### 3.2.3 Using Public Ledger

### 3.3 Perfomance

## 4. Conclusion
