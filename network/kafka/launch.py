import config
import sys
import os
import time

debug = True

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

def main():
    if len(sys.argv) < 1:
        print "python launch.py up: freshly Launch the kafka network"
        print "python launch.py down: Bring down the kafka network"
        return
    
    if sys.argv[1] == 'up':
        init_ZK()
        start_ZK()
        kfk_configs = []
        # kfk_configs = init_KFK() # Only call once for the first time setup
        start_KFK(kfk_configs)
    elif sys.argv[1] == 'down':
        stop_KFK()
        stop_ZK()
    else:
        print "Unrecognized Operation"



if __name__ == '__main__':
    main()
