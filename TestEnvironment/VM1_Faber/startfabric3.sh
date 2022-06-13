#!/bin/sh
# https://readthedocs.org/projects/fabric-v05/downloads/pdf/latest/
# https://hyperledger-fabric.readthedocs.io/pt/latest/test_network.html
# https://hyperledger.github.io/caliper/v0.4.2/fabric-tutorial/tutorials-fabric-existing/
grep stateDatabase ~/fabric-samples/test-network/core.yaml # should set do goleveldb
nvm use 10.24.1
npm -v
node -v
cd ~/fabric-samples/test-network
./network.sh up createChannel -c mychannel 
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript
cd ~/fabric-samples/asset-transfer-basic/application-javascript
npm install 
# node tokenapp.js init
cd
cd ~/fabric-samples/test-network
export PATH=${PWD}/../bin:${PWD}:$PATH
export FABRIC_CFG_PATH=$PWD/../config/

# Environment variables for Org1

export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051

peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C mychannel -n basic --peerAddresses localhost:7051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt --peerAddresses localhost:9051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt -c '{"function":"InitLedger","Args":[]}'
peer chaincode query -C mychannel -n basic -c '{"Args":["GetAllAssets"]}'
