#!/bin/sh
cd ~/dissertation/aries-cloudagent-python/demo
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo bob --cred-type=json-ld --events
