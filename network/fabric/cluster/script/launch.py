import config
import sys
import os
import time

debug=True

def remote_cmd(node, cmd):
    quoted_cmd = "\"" + cmd + "\""
    if debug:
        print "   ssh ", node, quoted_cmd
    cmd="ssh {} {}".format(node, quoted_cmd)
    os.system(cmd)



def kill_ps_aux(node, keyword):
    remote_cmd(node, "kill_ps_aux " + keyword)


def bash_rm(node, path):
    remote_cmd(node, "rm -rf " + path)


def bash_mkdir(node, path):
    remote_cmd(node, "mkdir -p " + path)


def bash_append_file(node, content, file):
    remote_cmd(node, "echo '{}' >> {} ".format(content, file))


def start_CA():
    print "Starting CA..."
    remote_cmd(config.CA_NODE, "docker-compose -f {} up -d ".format(config.CA_COMPOSE_FILE))


def stop_CA():
    print "Stopping CA..."
    remote_cmd(config.CA_NODE, "docker-compose -f {} down ".format(config.CA_COMPOSE_FILE))




def start_ZK():
    print "Start Zookeeper Nodes..."
    zk_nodes=[]
    zk_cmd_template="ZOO_MY_ID={} ZOO_DATADIR={} ZOO_CLIENTPORT={} zkServer.sh start " + config.ZK_CONFIGFILE
    zk_id = 1
    for i in range(config.ZK_START, config.ZK_END+1):
        zk_node="slave-" + str(i)
        zk_nodes.append(zk_node)
        zk_id = zk_id + 1


    for i, zk_node in enumerate(zk_nodes):
        zk_cmd=zk_cmd_template.format(i+1, config.ZK_DATA, config.ZK_PORT)
        remote_cmd(zk_node, zk_cmd)


def stop_ZK():
    print "Stop ZK..."
    for i in range(config.ZK_START, config.ZK_END+1):
        zk_node="slave-" + str(i)
        kill_ps_aux(zk_node, "zookeeper")


def init_ZK():
    '''
    Clear the ZK node
    Create the myid file
    Update the zookeeper property file.
    '''
    print "Initing zookeeper..."
    zk_nodes = []
    myid_cmd_template = "echo '{}' > {}"
    zk_id=1
    for i in range(config.ZK_START, config.ZK_END+1):
        zk_node="slave-" + str(i)
        zk_nodes.append(zk_node)
        bash_rm(zk_node, config.ZK_DATA)
        bash_mkdir(zk_node, config.ZK_DATA)

        # Create the myid file
        myid_path = config.ZK_DATA + "/myid"
        remote_cmd(zk_node, myid_cmd_template.format(zk_id, myid_path))

        # Update the correct property file
        remote_cmd(zk_node, "cp -r " + config.ZK_CONFIGFILE_TEMPLATE + " " + config.ZK_CONFIGFILE)
        zk_id = zk_id + 1


    property_update_cmd_template="echo 'server.{}={}:2888:3888' >> {}"
    for node in zk_nodes:
        for i, zk_node in enumerate(zk_nodes):
            property_update_cmd = property_update_cmd_template.format(i+1, zk_node, config.ZK_CONFIGFILE)
            remote_cmd(node, property_update_cmd)


def start_KFK(local_configs):
    if len(local_configs) == 0:
      kfk_id = 0
      for i in range(config.KFK_START, config.KFK_END+1):
        local_config = config.KFK_CONFIGFILE.format(kfk_id)
        local_configs.append(local_config)
        kfk_id = kfk_id + 1
    print "Start Kafka servers..."
    kfk_cmd_template = "kafka-server-start.sh {} "
    kfk_cmd_template += " > " + config.KFK_LOG + " 2>&1 "
    kfk_cmd_template += "&"

    kfk_id = 0
    for i in range(config.KFK_START, config.KFK_END+1):
        kfk_node = "slave-" + str(i)
        bash_rm(kfk_node, config.KFK_LOG)
        bash_rm(kfk_node, config.KFK_DATA)
        kfk_cmd = kfk_cmd_template.format(local_configs[kfk_id])
        remote_cmd(kfk_node, kfk_cmd)
        kfk_id = kfk_id + 1


def stop_KFK():
    print "Stop Kafka servers..."
    for i in range(config.KFK_START, config.KFK_END+1):
        zk_node="slave-" + str(i)
        kill_ps_aux(zk_node, "kafka")


def init_KFK():
    print "Initing Kafka..."
    zk_nodes = []
    for i in range(config.ZK_START, config.ZK_END+1):
        zk_node="slave-" + str(i) + ":" + str(config.ZK_PORT)
        zk_nodes.append(zk_node)

    kfk_id = 0
    local_kfk_configs = []
    for i in range(config.KFK_START, config.KFK_END+1):
        local_kfk_config = config.KFK_CONFIGFILE.format(kfk_id)
        local_kfk_configs.append(local_kfk_config)
        kfk_node="slave-" + str(i)
        remote_cmd(kfk_node, "cp -r " + config.KFK_CONFIGFILE_TEMPLATE + " " + local_kfk_config)
        bash_append_file(kfk_node, "message.max.bytes=103809024", local_kfk_config)
        bash_append_file(kfk_node, "replica.fetch.max.bytes=103809024", local_kfk_config)
        bash_append_file(kfk_node, "unclean.leader.election.enable=false", local_kfk_config)
        bash_append_file(kfk_node, "min.insync.replicas=2", local_kfk_config)
        bash_append_file(kfk_node, "default.replication.factor=3", local_kfk_config)
        bash_append_file(kfk_node, "zookeeper.connect=" + ",".join(zk_nodes), local_kfk_config)
        bash_append_file(kfk_node, "broker.id" + str(kfk_id), local_kfk_config)
        bash_append_file(kfk_node, "log.dir=" + config.KFK_DATA, local_kfk_config)
        kfk_id = kfk_id + 1

    return local_kfk_configs


def start_orderers():
    print "Removing orderers logs and data..."
    for i in range(config.ORDERER_START, config.ORDERER_END+1):
        orderer_node = "slave-" + str(i)
        bash_rm(orderer_node, config.ORDERER_DATA)
        bash_rm(orderer_node, config.ORDERER_LOG)

    print "Starting orderers..."
    orderer_cmd_template = "FABRIC_CFG_PATH=" + config.FABRIC_CFG_DIR + " "
    orderer_cmd_template += "ORDERER_GENERAL_LOGLEVEL=debug "
    orderer_cmd_template += "ORDERER_GENERAL_LISTENADDRESS=0.0.0.0 "
    orderer_cmd_template += "ORDERER_GENERAL_GENESISMETHOD=file "
    orderer_cmd_template += "ORDERER_GENERAL_GENESISFILE=" + config.ORDERER_GENESIS_BLK + " "
    orderer_cmd_template += "ORDERER_GENERAL_LOCALMSPID=OrdererMSP "
    orderer_cmd_template += "ORDERER_GENERAL_LOCALMSPDIR=" + config.ORDERER_LOCAL_MSPDIR_TEMPLATE + " "
    orderer_cmd_template += "ORDERER_KAFKA_RETRY_SHORTINTERVAL=1s "
    orderer_cmd_template += "ORDERER_KAFKA_RETRY_SHORTTOTAL=30s "
    orderer_cmd_template += "ORDERER_KAFKA_VERBOSE=true "
    orderer_cmd_template += "ORDERER_FILELEDGER_LOCATION=" + config.ORDERER_DATA + " "
    orderer_cmd_template += " orderer > " + config.ORDERER_LOG + " 2>&1 &"

    ordererID = 0
    for i in range(config.ORDERER_START, config.ORDERER_END+1):
        orderer_node = "slave-" + str(i)
        orderer_cmd = orderer_cmd_template.format(ordererID)
        remote_cmd(orderer_node, orderer_cmd)
        ordererID = ordererID + 1


def stop_orderers():
    print "Stop orderers..."
    for i in range(config.ORDERER_START, config.ORDERER_END+1):
        orderer_node = "slave-" + str(i)
        kill_ps_aux(orderer_node, "orderer")



def start_peers(peer_nodes):
    print "Remove peer's log and data..."
    for peer_node in peer_nodes:
        remote_cmd(peer_node, "removeUnwantedImages")
        remote_cmd(peer_node, "docker pull hyperledger/fabric-ccenv:1.3.0")
        remote_cmd(peer_node, "docker pull hyperledger/fabric-ccenv:latest")
        bash_rm(peer_node, config.PEER_DATA)
        bash_rm(peer_node, config.PEER_LOG)

    print "Start peers..."
    peer_cmd_template = "FABRIC_CFG_PATH=" + config.FABRIC_CFG_DIR + " "
    peer_cmd_template += "CORE_LOGGING_PEER=debug "
    peer_cmd_template += "CORE_PEER_ENDORSER_ENABLED=true "
    peer_cmd_template += "CORE_LOGGING_LEVEL=DEBUG "
    peer_cmd_template += "CORE_PEER_GOSSIP_USELEADERELECTION=true "
    peer_cmd_template += "CORE_PEER_GOSSIP_ORGLEADER=false "
    peer_cmd_template += "CORE_PEER_ID=peer0.org{}.example.com "
    peer_cmd_template += "CORE_PEER_ADDRESS=localhost:7051 "
    peer_cmd_template += "CORE_PEER_GOSSIP_EXTERNALENDPOINT=localhost:7051 "
    peer_cmd_template += "CORE_PEER_LOCALMSPID=Org{}MSP "
    peer_cmd_template += "CORE_PEER_MSPCONFIGPATH=" + config.PEER_LOCAL_MSPDIR_TEMPLATE + " "
    peer_cmd_template += "CORE_PEER_FILESYSTEMPATH=" + config.PEER_DATA + " "
    peer_cmd_template += "peer node start > " + config.PEER_LOG + " 2>&1 &"

    peerID = 1
    for peer_node in peer_nodes:
        remote_cmd(peer_node, peer_cmd_template.format(peerID, peerID, peerID, peerID))
        peerID = peerID + 1


def stop_peers(peer_nodes):
    print "Stop peers..."
    for peer_node in peer_nodes:
        kill_ps_aux(peer_node, "peer")


def init_peers(peer_nodes):
    print "Initing Peers..."
    for peer_node in peer_nodes:
        remote_cmd(peer_node, "docker pull hyperledger/fabric-ccenv:1.3.0")


def start_zk_clients():
    zk_node="slave-" + str(config.ZK_START) + ":2181"
    print "Start zk clients with zk node " + zk_node
    cli_cmd = " node " + config.ZK_CLI_SCRIPT + " " + zk_node
    cli_cmd += " > " + config.ZK_CLI_LOG + " 2>&1 "
    cli_cmd += "&"
    for i in range(config.CLI_START, config.CLI_END+1):
        cli_node = "slave-" + str(i)
        remote_cmd(cli_node, cli_cmd)


def main():
    if len(sys.argv) < 2:
        print "python launch.py <cluster_dir> up: freshly Launch the network"
        print "python launch.py <cluster_dir> down: Bring down the network"
        return

    cluster_dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(cluster_dir):
       print "Cluster Directory {} Not Found".format(cluster_dir)
       return
    
    # Update relevant parameters in config
    config.CRYPTO_CFG_DIR=os.path.join(cluster_dir, "crypto_config")
    config.CHANNEL_ARTIFACT_DIR=os.path.join(cluster_dir, "channel_artifacts")
    config.ORDERER_GENESIS_BLK=os.path.join(config.CHANNEL_ARTIFACT_DIR, "genesis.block")
    config.ORDERER_LOCAL_MSPDIR_TEMPLATE=os.path.join(config.CRYPTO_CFG_DIR, "ordererOrganizations/example.com/orderers/orderer{}.example.com/msp")
    config.PEER_LOCAL_MSPDIR_TEMPLATE=os.path.join(config.CRYPTO_CFG_DIR,"peerOrganizations/org{}.example.com/peers/peer0.org{}.example.com/msp")

    peer_info_path = os.path.join(cluster_dir, "nodes.txt")
    with open(peer_info_path, 'r') as f:
      raw_peer_nodes = f.readlines()
    peer_nodes = [peer_node.strip() for peer_node in raw_peer_nodes]

    if sys.argv[2] == "up":
        init_ZK()
        start_ZK()
        kfk_configs = []
#        kfk_configs = init_KFK()
        start_KFK(kfk_configs)

#        start_CA()

        start_orderers()

#        init_peers(peer_nodes)
        start_peers(peer_nodes)
#        if sys.argv[2] == "zk": 
		#	start_zk_clients()
    elif sys.argv[2] == "down":
        stop_peers(peer_nodes)
        stop_orderers()
#        stop_CA()
        stop_KFK()
        stop_ZK()
    else:
        print "Unrecognized option ", argv


if __name__ == '__main__':
    main()

