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


 function removeUnwantedImages() {
   DOCKER_IMAGE_IDS=$(docker images | awk '($1 ~ /dev-peer*/) {print $3}')
   if [ -z "$DOCKER_IMAGE_IDS" -o "$DOCKER_IMAGE_IDS" == " " ]; then
     echo "---- No images available for deletion ----"
   else
     docker rmi -f $DOCKER_IMAGE_IDS
   fi
 }
"""

CLUSTER_DIR="/users/ruanpc/caliper/network/fabric/cluster"

# ZK_START=40
# ZK_END=42
# ZK_PORT=2181
# ZK_DATA="/data/ruanpc/zookeeper"
# ZK_CONFIGFILE_TEMPLATE=CLUSTER_DIR+"/zk-config/zookeeper.properties.template"
# ZK_CONFIGFILE=CLUSTER_DIR+"/zk-config/zookeeper.properties"

# KFK_DATA="/data/ruanpc/kafka"
# KFK_START=40
# KFK_END=43
# KFK_CONFIGFILE_TEMPLATE=CLUSTER_DIR+"/kafka-config/server.properties.template"
# KFK_CONFIGFILE=CLUSTER_DIR+"/kafka-config/server-{}.properties"
# KFK_LOG="/data/ruanpc/kafka_log"

# CA_NODE="slave-6"
# CA_COMPOSE_FILE=EXP_DIR+"/ca-docker-compose.yaml"

FABRIC_CFG_DIR=CLUSTER_DIR+"/fabric-config"


ORDERER_START=30
ORDERER_END=31
ORDERER_DATA="/data/ruanpc/hyperledger/production/orderer"
ORDERER_LOG="/data/ruanpc/orderer"

# PEER_START=4
# PEER_END=5
PEER_DATA="/data/ruanpc/hyperledger/production/peer"
PEER_LOG="/data/ruanpc/peer"

# # Config one of zk node address in config.json
# ZK_CLI_SCRIPT="/users/ruanpc/caliper/src/comm/client/zoo-client.js"
# CLI_START=12
# CLI_END=13
# ZK_CLI_LOG="/data/ruanpc/zk_cli_log"


# TO be configured by launch.py based on the given parameters
CRYPTO_CFG_DIR=""
CHANNEL_ARTIFACT_DIR=""

ORDERER_GENESIS_BLK=""
ORDERER_LOCAL_MSPDIR_TEMPLATE=""
PEER_LOCAL_MSPDIR_TEMPLATE=""
