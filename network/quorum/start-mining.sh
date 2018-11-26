#!/bin/bash
# node_num
cd `dirname ${BASH_SOURCE-$0}`
. env.sh
echo "[*] start-mining.sh"

let i=$1+1

PRIVATE_CONFIG=ignore nohup ${QUORUM} --datadir $QUO_DATA/dd$i  --nodiscover --verbosity 5 --networkid 17 --raft --rpc --rpcaddr 0.0.0.0 --rpcapi admin,db,eth,debug,miner,net,shh,txpool,personal,web3,quorum,raft --emitcheckpoints --raftport 50400 --rpcport 8000 --port 9000 --raftblocktime 2000 --unlock 0 --password <(echo -n "") > $LOG_DIR/logs 2>&1 &
#echo --datadir $QUO_DATA --rpc --rpcaddr 0.0.0.0 --rpcport 8000 --port 9000 --raft --raftport 50400 --raftblocktime 2000 --unlock 0 --password <(echo -n "") 
echo "[*] miner started"
sleep 1

#for com in `cat $QUO_HOME/addPeer.txt`; do
 #    geth --exec "eth.blockNumber" attach $QUO_DATA/geth.ipc
     #geth  attach ipc:/$ETH_DATA/geth.ipc
#done
