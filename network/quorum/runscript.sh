# <web3_script_path> <node_num>
cd `dirname ${BASH_SOURCE-$0}`

. env.sh

PRIVATE_CONFIG=${QUO_DATA}/c${2}/tm.ipc geth --exec "loadScript(\"$1\")" attach ipc:${QUO_DATA}/dd${2}/geth.ipc
