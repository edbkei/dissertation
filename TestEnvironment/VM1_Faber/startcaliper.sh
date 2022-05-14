#!/bin/sh
# cd ~/projects/caliper-workspace3/benchmarks$ nano myAssetBenchmark.yaml
cd ~/go/src/github.com/edbkei/caliper-workspace3
npx caliper launch manager --caliper-workspace ./ --caliper-networkconfig networks/networkConfig.yaml --caliper-benchconfig benchmarks/myAssetBenchmark.yaml --caliper-flow-only-test --caliper-fabric-gateway-enabled
