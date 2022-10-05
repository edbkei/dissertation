#!/bin/sh
# Revocation: https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/README.md
# tail server: https://github.com/hyperledger/aries-cloudagent-python/blob/main/demo/AliceGetsAPhone.md#run-an-instance-of-indy-tails-server
cd
cd ~/dissertation/indy-tails-server/docker
./manage up
cd
cd ~/dissertation/aries-cloudagent-python/demo
#TAILS_NETWORK=docker_tails-server LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io  ./run_demo faber --aip 20 --revocation --events
TAILS_NETWORK=docker_tails-server LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io  ./run_demo faber --aip 20 --revocation  
