#!/bin/bash
# <node_num> -p
cd `dirname ${BASH_SOURCE-$0}`
. env.sh
echo "[*] start-mining.sh"

let i=$1+1
if [[ $2 == "-p" ]]; then
  PRIVATE_CONFIG=${QUO_DATA}/c${i}/tm.ipc nohup ${QUORUM} --datadir $QUO_DATA/dd$i  --nodiscover --verbosity 5 --networkid 17 --raft --rpc --rpcaddr 0.0.0.0 --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,raft --emitcheckpoints --permissioned --raftport 50400 --rpcport 8000 --port 9000 --raftblocktime 2000 --unlock 0 --password <(echo -n "") > $LOG_DIR/logs 2>&1 &
  echo "[*] Permissioned miner started"
else
  PRIVATE_CONFIG=ignore nohup ${QUORUM} --datadir $QUO_DATA/dd$i  --nodiscover --verbosity 5 --networkid 17 --raft --rpc --rpcaddr 0.0.0.0 --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,raft --emitcheckpoints --permissioned --raftport 50400 --rpcport 8000 --port 9000 --raftblocktime 2000 --unlock 0 --password <(echo -n "") > $LOG_DIR/logs 2>&1 &
  echo "[*] miner started"
fi
#echo --datadir $QUO_DATA --rpc --rpcaddr 0.0.0.0 --rpcport 8000 --port 9000 --raft --raftport 50400 --raftblocktime 2000 --unlock 0 --password <(echo -n "") 
sleep 1

#for com in `cat $QUO_HOME/addPeer.txt`; do
 #    geth --exec "eth.blockNumber" attach $QUO_DATA/geth.ipc
     #geth  attach ipc:/$ETH_DATA/geth.ipc

#done