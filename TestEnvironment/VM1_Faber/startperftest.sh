#!/bin/sh
read -p "Type 0:von-network (local) 1: http://dev.greenlight.bcovrin.vonx.io 2:http://prod.bcovrin.vonx.io/: " ledger
read -p "Type number of threads (concurrent credential exchanges): " threads
read -p "Type the number of credentials: " count
cd ~/dissertation/aries-cloudagent-python/demo
echo $ledger
echo $threads
echo $count
if [ $ledger -eq 0 ]
then
  echo "ledger 0"
elif [ $ledger -eq 1 ]
then
  echo "ledger 1"
else
  echo "ledger 0"
fi
