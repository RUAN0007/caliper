"""
Preliminaries:
  Number of orderers, peers are correctly configured in crypto-config.yaml.
  Crypto-material should be corrected generated.

  Addresses of kafka nodes, peers node are corrected configured in configtx.yaml
  genesis block should be corrected generated.


  For all peer node, make sure to have hyperledger/fabric-ccenv:1.2.0 docker images

  Two bash functions are visible in shell
    kill_ps_aux() {
      description=$1
      ps aux | grep "$description" | awk '{print $2}' |  xargs kill -9
    }
"""

CLUSTER_DIR="/users/ruanpc/caliper/network/kafka"

ZK_START=40
ZK_END=42
ZK_PORT=2181
ZK_DATA="/data/ruanpc/zookeeper"
ZK_CONFIGFILE_TEMPLATE=CLUSTER_DIR+"/zk-config/zookeeper.properties.template"
ZK_CONFIGFILE=CLUSTER_DIR+"/zk-config/zookeeper.properties"

KFK_DATA="/data/ruanpc/kafka"
KFK_START=40
KFK_END=43
KFK_CONFIGFILE_TEMPLATE=CLUSTER_DIR+"/kafka-config/server.properties.template"
KFK_CONFIGFILE=CLUSTER_DIR+"/kafka-config/server-{}.properties"
KFK_LOG="/data/ruanpc/kafka_log"

