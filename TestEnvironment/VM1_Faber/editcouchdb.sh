#!/bin/sh
PATHCORE=~/go/src/github.com/edbkei/fabric-samples/config/core.yaml
grep stateDatabase $PATHCORE
echo $PATHCORE


nano ~/go/src/github.com/edbkei/fabric-samples/config/core.yaml

grep stateDatabase $PATHCORE
echo $PATHCORE

