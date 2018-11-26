#!/bin/bash
#args: node_num node_count
cd `dirname ${BASH_SOURCE-$0}`
. env.sh

let i=$1+1

echo "[*] init.sh"
mkdir -p $LOG_DIR
mkdir -p $QUO_DATA/dd$i/{keystore,geth}

cp keys/key$i $QUO_DATA/dd$i/keystore
cp raft/static-nodes$2.json $QUO_DATA/dd$i/static-nodes.json
cp raft/nodekey$i $QUO_DATA/dd$i/geth/nodekey
${QUORUM} --datadir=$QUO_DATA/dd$i init $QUO_HOME/genesis_quorum.json