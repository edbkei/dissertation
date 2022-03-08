#!/bin/sh
cd ~/go/src/github.com/edbkei/fabric-samples/test-network
./network.sh down
cd ~/go/src/github.com/edbkei/fabric-samples/asset-transfer-basic/application-javascript
rm -r wallet
docker ps -a
