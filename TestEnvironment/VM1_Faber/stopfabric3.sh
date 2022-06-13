#!/bin/sh
cd ~/fabric-samples/test-network
./network.sh down
cd ~/fabric-samples/asset-transfer-basic/application-javascript
rm -r wallet
docker ps -a
