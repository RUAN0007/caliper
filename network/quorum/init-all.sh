#!/bin/bash
# node_count
cd `dirname ${BASH_SOURCE-$0}`
. env.sh

echo "[*] init-all"
mkdir -p $LOG_DIR

i=0
for host in `cat $HOSTS`; do
  if [[ $i -lt $1 ]]; then
    echo [*] Configuring node $i on host $host
    ssh -oStrictHostKeyChecking=no  ruanpc@$host $QUO_HOME/init.sh $i $1
    echo done node $host
  fi
  let i=$i+1
done