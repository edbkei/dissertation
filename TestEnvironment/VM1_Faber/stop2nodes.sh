#!/bin/sh
cd ~/go/src/github.com/edbkei/fabric-samples/test-network
./network.sh down
docker ps -a
