# https://hyperledger-fabric.readthedocs.io/en/release-2.2/write_first_app.html
PATHCORE=~/go/src/github.com/edbkei/fabric-samples/config/core.yaml
grep stateDatabase $PATHCORE
echo $PATHCORE
cd
cd ~/go/src/github.com/edbkei/fabric-samples/test-network
./network.sh up createChannel -c mychannel -ca
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
cd ../asset-transfer-basic/application-javascript
npm install
node tokenapp.js
node tokenapp.js init
