#!/bin/sh
cd ~/go/src/github.com/edbkei/fabric-samples4/test-network
./network.sh down
cd ~/go/src/github.com/edbkei/fabric-samples4/asset-transfer-basic/application-javascript
rm -r wallet
docker ps -a
