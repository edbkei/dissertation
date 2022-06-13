#!/bin/sh

# https://hyperledger-fabric.readthedocs.io/en/release-2.2/deploy_chaincode.html
# https://hyperledger-fabric.readthedocs.io/en/release-2.2/channel_update_tutorial.html
#
#read -p "Type channel number: " CHANNEL
CHANNEL=5
grep stateDatabase ~/go/src/github.com/edbkei/fabric-samples/config/core.yaml
cd
cd ~/go/src/github.com/edbkei/fabric-samples/test-network
./network.sh down
./network.sh up createChannel -c channel$CHANNEL
# ADDORG3
# setup the environment
# Generate the Org3 Crypto Material
cd addOrg3
./addOrg3.sh up -c channel$CHANNEL
cd ..
./network.sh down
./network.sh up createChannel -c channel$CHANNEL
cd addOrg3
../../bin/cryptogen generate --config=org3-crypto.yaml --output="../organizations"
export FABRIC_CFG_PATH=$PWD
../../bin/configtxgen -printOrg Org3MSP > ../organizations/peerOrganizations/org3.example.com/org3.json
# cd 
# cd ~/fabric-samples/test-network/addOrg3
# cp -r docker ../../../go/src/github.com/edbkei/fabric-samples/test-network/addOrg3
docker-compose -f docker/docker-compose-org3.yaml up -d
cd ..
export PATH=${PWD}/../bin:$PATH
export FABRIC_CFG_PATH=${PWD}/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
peer channel fetch config channel-artifacts/config_block.pb -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com -c channel$CHANNEL --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
# Convert the configuration to JSON and Trim it down
cd channel-artifacts
configtxlator proto_decode --input config_block.pb --type common.Block --output config_block.json
jq .data.data[0].payload.data.config config_block.json > config.json
jq -s '.[0] * {"channel_group":{"groups":{"Application":{"groups": {"Org3MSP":.[1]}}}}}' config.json ../organizations/peerOrganizations/org3.example.com/org3.json > modified_config.json
configtxlator proto_encode --input config.json --type common.Config --output config.pb
configtxlator proto_encode --input modified_config.json --type common.Config --output modified_config.pb
configtxlator compute_update --channel_id channel$CHANNEL --original config.pb --updated modified_config.pb --output org3_update.pb
configtxlator proto_decode --input org3_update.pb --type common.ConfigUpdate --output org3_update.json
echo '{"payload":{"header":{"channel_header":{"channel_id":"'channel$CHANNEL'", "type":2}},"data":{"config_update":'$(cat org3_update.json)'}}}' | jq . > org3_update_in_envelope.json
configtxlator proto_encode --input org3_update_in_envelope.json --type common.Envelope --output org3_update_in_envelope.pb
# Sign and Submit the Config Update
cd ..
peer channel signconfigtx -f channel-artifacts/org3_update_in_envelope.pb
# Export the org2 environment variables
# you can issue all of these commands at once
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_ADDRESS=localhost:9051
peer channel update -f channel-artifacts/org3_update_in_envelope.pb -c channel$CHANNEL -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
# if needed, docker logs -f peer0.org1.example.com
# Join Org3 to the Channel
# you can issue all of these commands at once
#export PATH=${PWD}/../bin:$PATH
#export FABRIC_CFG_PATH=$PWD/../config/
export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org3MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=${PWD}/organizations/peerOrganizations/org3.example.com/users/Admin@org3.example.com/msp
export CORE_PEER_ADDRESS=localhost:11051
peer channel fetch 0 channel-artifacts/channel$CHANNEL.block -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com -c channel$CHANNEL --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
peer channel join -b channel-artifacts/channel$CHANNEL.block # response 500
# https://stackoverflow.com/questions/67271160/hyperledger-error-cannot-create-ledger-from-genesis-block-ledger-mychannel
# IF NEEDED: network.sh down, and docker system prune --volumes -f
# OR POSSIBLY: https://stackoverflow.com/questions/52019932/hyperledger-fabric-peer-join-fails-with-bad-proposal-response
#
# Configurig Leader Election
CORE_PEER_GOSSIP_USELEADERELECTION=false
CORE_PEER_GOSSIP_ORGLEADER=true
CORE_PEER_GOSSIP_USELEADERELECTION=true
CORE_PEER_GOSSIP_ORGLEADER=false
cd ../asset-transfer-basic/chaincode-javascript
npm install
cd ../../test-network
./network.sh deployCC -ccn basic -ccp ../asset-transfer-basic/chaincode-javascript/ -ccl javascript -c channel$CHANNEL
peer lifecycle chaincode package basic.tar.gz --path ../asset-transfer-basic/chaincode-javascript/ --lang node --label basic_1
peer lifecycle chaincode install basic.tar.gz
peer lifecycle chaincode queryinstalled > temp.txt
cat temp.txt | grep ID | sed -rn 's/.*(basic_1:[^;}]+).*/\1/p' | cut -f1 -d"," > temp2.txt
PacketID=`cat temp2.txt`
echo $PacketID
rm temp.txt
rm temp2.txt
export CC_PACKAGE_ID=$PacketID
echo $CC_PACKAGE_ID
# use the --package-id flag to provide the package identifier
# use the --init-required flag to request the ``Init`` function be invoked to initialize the chaincode
peer lifecycle chaincode approveformyorg -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem --channelID channel$CHANNEL --name basic --version 1.0 --package-id $CC_PACKAGE_ID --sequence 1
# use the --name flag to select the chaincode whose definition you want to query
peer lifecycle chaincode querycommitted --channelID channel$CHANNEL --name basic --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem
peer chaincode invoke -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com --tls --cafile ${PWD}/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem -C channel$CHANNEL -n basic --peerAddresses localhost:9051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt --peerAddresses localhost:11051 --tlsRootCertFiles ${PWD}/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt -c '{"function":"InitLedger","Args":[]}'
peer chaincode query -C channel$CHANNEL -n basic -c '{"Args":["GetAllAssets"]}'










