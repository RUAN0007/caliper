#!/bin/bash

# must be executed under ~/caliper/benchmark/ycsb
set -o pipefail # Save exit code after pipelining to tee
RETRY_LIMIT=1
# for NODE_COUNT in 9; do
for NODE_COUNT in 1 3 5 7 9 11; do
  EXP_DIR=/data/ruanpc/quorum-exp/scale/node-${NODE_COUNT}
  mkdir -p ${EXP_DIR}
  ../../network/quorum/stop-all.sh 11
  for path in quorum-env/sc-config/node-${NODE_COUNT}/*; do
    filename=$(basename -- "$path")
    ../../network/quorum/init-all.sh ${NODE_COUNT} -p; 
    sleep 5;
    ../../network/quorum/start-all.sh ${NODE_COUNT} -p;
    echo "======================Experiment for $filename with $NODE_COUNT nodes=========================="
    timeout 120m node main.js -c $path -n  ../../../../../data/ruanpc/qdata/setup.json | tee ${EXP_DIR}/${filename}.log
    # rc=$?
    # i=1
    # while [[ $rc -ne 0 ]] && [[ $i -le $RETRY_LIMIT ]];
    # do
    #   echo "Retry..." $i
    #   ../../network/quorum/stop-all.sh ${NODE_COUNT}; ../../network/quorum/init-all.sh ${NODE_COUNT} -p; ../../network/quorum/start-all.sh ${NODE_COUNT} -p;
    #   node main.js -c $path -n  ../../../../../data/ruanpc/qdata/setup.json | tee ${EXP_DIR}/${filename}.log.${i}
    #   rc=$?
    #   let i=$i+1
    # done

    echo "=============================================================================="

    ../../network/quorum/stop-all.sh ${NODE_COUNT};
  done
done

