#!/bin/bash

# must be executed under ~/caliper/benchmark/ycsb
set -o pipefail # Save exit code after pipelining to tee
EXP_DIR=/data/ruanpc/quorum-exp/macro
RETRY_LIMIT=3
mkdir -p ${EXP_DIR}
../../network/quorum/stop-all.sh 5;
for path in quorum-env/macro-config/*; do
  filename=$(basename -- "$path")
  ../../network/quorum/init-all.sh 5 -p; ../../network/quorum/start-all.sh 5 -p;
  echo "======================Experiment for ", $filename, "=========================="
  node main.js -c $path -n  ../../../../../data/ruanpc/qdata/setup.json | tee ${EXP_DIR}/${filename}.log
  rc=$?
  i=1

  while [[ $rc -ne 0 ]] && [[ $i -le $RETRY_LIMIT ]];
  do
    echo "Retry..." $i
    ../../network/quorum/stop-all.sh 5; ../../network/quorum/init-all.sh 5 -p; ../../network/quorum/start-all.sh 5 -p;
    node main.js -c $path -n  ../../../../../data/ruanpc/qdata/setup.json | tee ${EXP_DIR}/${filename}.log.${i}
    rc=$?
    let i=$i+1
  done

  echo "=============================================================================="

  ../../network/quorum/stop-all.sh 5;
done
