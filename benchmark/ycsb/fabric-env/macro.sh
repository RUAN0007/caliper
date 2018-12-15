#!/bin/bash

# must be executed under ~/caliper/benchmark/ycsb
EXP_DIR=/data/ruanpc/fabric-exp/macro
mkdir -p ${EXP_DIR}
for path in fabric-env/macro-config/*; do
  filename=$(basename -- "$path")
  python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/5p up;
  echo "======================Experiment for ", $filename, "=========================="
  node main.js -c $path -n ../../network/fabric/cluster/env/5p/setup.json | tee ${EXP_DIR}/${filename}.log
  echo "=============================================================================="

  python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/5p down;
done