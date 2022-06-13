#!/bin/sh
#export COMPOSE_HTTP_TIMEOUT=420
cd ~/go/src/github.com/edbkei/fabric-samples/test-network
./network.sh up createChannel -c mychannel -ca
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
cd ~/go/src/github.com/edbkei/fabric-samples/asset-transfer-basic/application-javascript
npm install 
node tokenapp.js init
