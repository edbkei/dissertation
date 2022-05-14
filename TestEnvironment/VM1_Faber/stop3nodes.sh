#!/bin/sh
# https://hyperledger-fabric.readthedocs.io/en/release-2.2/deploy_chaincode.html
# https://hyperledger-fabric.readthedocs.io/en/release-2.2/channel_update_tutorial.html
#
cd
cd ~/go/src/github.com/edbkei/fabric-samples/test-network
./network.sh down
docker system prune --volumes -f
docker kill $(docker ps -qa)
docker rm $(docker ps -qa)
docker system prune
docker ps
