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
