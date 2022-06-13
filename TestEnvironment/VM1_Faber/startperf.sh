#!/bin/sh
read -p "Type 0:von-network (local) 1: http://dev.greenlight.bcovrin.vonx.io 2:http://prod.bcovrin.vonx.io/: " ledger
read -p "Type number of threads (concurrent credential exchanges): " threads
read -p "Type the number of credentials: " count
cd ~/dissertation/aries-cloudagent-python/demo
if [ $ledger -eq 0 ]
then
  ./run_demo performance --count $count --threads $threads
elif [ $ledger -eq 1 ] 
then
  LEDGER_URL=http://dev.greenlight.bcovrin.vonx.io ./run_demo performance --count $count --threads $threads
else
  LEDGER_URL=http://prod.bcovrin.vonx.io ./run_demo performance --count $count --threads $threads
fi
