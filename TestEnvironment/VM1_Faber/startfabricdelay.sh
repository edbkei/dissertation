#!/bin/sh
export COMPOSE_HTTP_TIMEOUT=420
export FABRIC_START_TIMEOUT=90
PATHCORE=~/go/src/github.com/edbkei/fabric-samples4/config/core.yaml
echo $PATHCORE
grep stateDatabase $PATHCORE
cd ~/go/src/github.com/edbkei/fabric-samples4/test-network
./network.sh up createChannel -c mychannel -ca
#./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
#cd ~/go/src/github.com/edbkei/fabric-samples/asset-transfer-basic/application-javascript
#npm install 
#node tokenapp.js init
