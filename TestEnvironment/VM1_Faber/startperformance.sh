#!/bin/sh
cd ~/dissertation/aries-cloudagent-python/demo
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance --count 500 --threads 100
