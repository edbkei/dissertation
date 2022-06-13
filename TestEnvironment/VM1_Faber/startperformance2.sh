#!/bin/sh
cd ~/aries-cloudagent-python/demo
LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance --count 10 --threads 10
