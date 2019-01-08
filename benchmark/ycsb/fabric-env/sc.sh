#!/bin/bash

# must be executed under ~/caliper/benchmark/ycsb
set -o pipefail # Save exit code after pipelining to tee

for NODE_COUNT in 1 3 5 7 9 11; do
# for NODE_COUNT in 1; do
  if [ -d fabric-env/scale/node-${NODE_COUNT} ] 
  then
    EXP_DIR=/data/ruanpc/fabric-exp/scale/node-${NODE_COUNT}
    mkdir -p ${EXP_DIR}
    python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/${NODE_COUNT}p down;
    for path in fabric-env/scale/node-${NODE_COUNT}/*; do
      filename=$(basename -- "$path")
      python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/${NODE_COUNT}p up;
      echo "======================Experiment for ", $filename, "with ", $NODE_COUNT, "=========================="
      timeout 120m node main.js -c $path -n ../../network/fabric/cluster/env/${NODE_COUNT}p/setup.json | tee ${EXP_DIR}/${filename}.log
      echo "=============================================================================="

      python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/${NODE_COUNT}p down;
    done
  fi
done