import sys
import os
import yaml
import json
from pprint import pprint
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

channel_name = "rpcchannel"
caliper_home_dir = '/users/ruanpc/caliper/'

def get_filepath_in_dir(dir_abspath):
  # Get the unique file under dir_path
  d = os.listdir(dir_abspath)
  return os.path.join(dir_abspath, d[0])

def main():
  if len(sys.argv) <= 3:
    print " Usage: <directory> <peer_node1> <peer_node2> ... "
    return
  directory_name = sys.argv[1]
  peer_nodes = sys.argv[2:] 
  node_count = len(peer_nodes)

  cluster_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  template_dir = os.path.join(cluster_dir, "template")

  # Step 1: Make target new directory under cluster
  new_dir = os.path.abspath(directory_name)
  os.mkdir(new_dir)  
  
  # Step 2: Prepare crypto_config.yaml from template
  with open(os.path.join(template_dir, "crypto_config.yaml.template")) as f:
    crypto_config = yaml.load(f, Loader=Loader)
  peer_orgs = crypto_config["PeerOrgs"]
  
  for i in range(2, node_count+1):
    peer_org = peer_orgs[0].copy()
    peer_org["Domain"] = "org{}.example.com".format(i)
    peer_org["Name"] = "Org{}".format(i)
    peer_orgs.append(peer_org)
  crypto_config["PeerOrgs"] = peer_orgs
  
  crypto_yaml = os.path.join(new_dir, "crypto_config.yaml")
  with open(crypto_yaml, 'w') as f:
    yaml.dump(crypto_config, f, default_flow_style=False)
  
  # Step 3: Prepare configtx.yaml from template
  with open(os.path.join(template_dir, "configtx.yaml.template")) as f:
    configtx = yaml.load(f, Loader=Loader)
  #pprint(configtx)
  orderer_org = configtx["Organizations"][0]
  peer_org = configtx["Organizations"][1]
  # print orderer_org
  orderer_org_msp = os.path.join(new_dir, "crypto_config/ordererOrganizations/example.com/msp")
  orderer_org['MSPDir'] = orderer_org_msp
  # print orderer_org

  peer_orgs = [] 
  for i in range(1, node_count+1):
    peer_org = {}
    peer_org['Name'] = "Org{}MSP".format(i)
    peer_org['ID'] = "Org{}MSP".format(i)
    peer_org['AnchorPeers'] = [{'Host': peer_nodes[i-1], 'Port': 7051}]
    peer_org_msp = os.path.join(new_dir, "crypto_config/peerOrganizations/org{}.example.com/msp".format(i)) 
    peer_org['MSPDir'] = peer_org_msp
    peer_orgs.append(peer_org)
  # print peer_orgs

  configtx["Organizations"] = [orderer_org]
  [configtx["Organizations"].append(peer_org) for peer_org in peer_orgs]
    
  configtx["Profiles"]["OrgsOrdererGenesis"]["Orderer"]["Organizations"] = [orderer_org]
  configtx["Profiles"]["OrgsOrdererGenesis"]["Consortiums"]["SampleConsortium"]["Organizations"] = peer_orgs
  configtx["Profiles"]["OrgsChannel"]["Application"]["Organizations"] = peer_orgs
  
  configtx_yaml = os.path.join(new_dir, "configtx.yaml")
  with open(configtx_yaml, 'w') as f:
    yaml.dump(configtx, f, default_flow_style=False)
  #pprint(configtx)
  
  crypto_dir = os.path.join(new_dir, "crypto_config")
  os.mkdir(crypto_dir)
  cmd = "cryptogen generate --output={} --config={}".format(crypto_dir, crypto_yaml)
  # print cmd
  os.system(cmd)
  
  artifact_dir = os.path.join(new_dir, "channel_artifacts")
  os.mkdir(artifact_dir)

  blk_path = os.path.join(artifact_dir, "genesis.block")
  genesis_cmd = "configtxgen --configPath={} -profile OrgsOrdererGenesis -outputBlock {} ".format(new_dir, blk_path)
  os.system(genesis_cmd)
  
  configtx_path = os.path.join(artifact_dir, "channel.tx") 
  txn_cmd = " configtxgen --configPath={} -profile OrgsChannel -outputCreateChannelTx {} -channelID {}".format(new_dir, configtx_path, channel_name)
  os.system(txn_cmd)

# Step 4: Prepare setup.json
  with open(os.path.join(template_dir, "setup.json.template")) as f:
    setup_config = json.load(f)
  #pprint (setup_config)
  
  # Change to relative path for the rest of code
  rel_crypto_dir = os.path.relpath(crypto_dir, caliper_home_dir)
  rel_configtx_path = os.path.relpath(configtx_path, caliper_home_dir)

  # To configure network field
  setup_config['fabric']['cryptodir'] = rel_crypto_dir
  key_absdir = os.path.join(crypto_dir, 'ordererOrganizations/example.com/users/Admin@example.com/msp/keystore/')
  for i in range(2): # two orderers
    key_abspath = get_filepath_in_dir(key_absdir)
    rel_keypath= os.path.relpath(key_abspath,caliper_home_dir)

    setup_config['fabric']['network']['orderers'][i]['user']['key'] = rel_keypath
    setup_config['fabric']['network']['orderers'][i]['user']['cert'] = os.path.join(rel_crypto_dir, 'ordererOrganizations/example.com/users/Admin@example.com/msp/signcerts/Admin@example.com-cert.pem')
    setup_config['fabric']['network']['orderers'][i]['tls_cacerts'] = os.path.join(rel_crypto_dir, 'ordererOrganizations/example.com/users/Admin@example.com/tls/ca.crt')

  for idx in range(1, node_count+1):  
    org_config = {}
    org_config['name'] = 'peerOrg{}'.format(idx)
    org_config['mspid'] = 'Org{}MSP'.format(idx)
    org_config['user'] = {}
    
    key_absdir = os.path.join(crypto_dir, "peerOrganizations/org{}.example.com/users/Admin@org{}.example.com/msp/keystore/".format(idx, idx))
    key_abspath = get_filepath_in_dir(key_absdir)    
    rel_keypath = os.path.relpath(key_abspath, caliper_home_dir)
    org_config['user']['key'] = rel_keypath
    org_config['user']['cert'] = os.path.join(rel_crypto_dir, 'peerOrganizations/org{}.example.com/users/Admin@org{}.example.com/msp/signcerts/Admin@org{}.example.com-cert.pem'.format(idx, idx, idx))
    org_config['peer0'] = {} # Single peer in each org
    org_config['peer0']['requests'] = 'grpc://{}:7051'.format(peer_nodes[idx-1])
    org_config['peer0']['server-hostname'] = 'peer0.org{}.example.com'.format(idx)
    org_config['peer0']['tls_cacerts'] = os.path.join(rel_crypto_dir, "peerOrganizations/org{}.example.com/peers/peer0.org{}.example.com/tls/ca.crt".format(idx,idx))
    
    org_name = "org{}".format(idx)
    setup_config['fabric']['network'][org_name] = org_config

  
  # To configure channel field
  setup_config['fabric']['channel'][0]['name'] = channel_name
  setup_config['fabric']['channel'][0]['organizations'] = ["org{}".format(i) for i in range(1, node_count+1)]
  setup_config['fabric']['channel'][0]['config'] = rel_configtx_path
  
  # To configure endorsement policy 
  identities = []
  policy = []
  for idx in range(node_count):
    identity = {}
    identity['role'] = {}
    identity['role']['name'] = 'member'
    identity['role']['mspId'] = 'Org{}MSP'.format(idx+1)
    identities.append(identity)
    
    policy.append({'signed-by': idx})
  
  setup_config['fabric']['endorsement-policy']['identities'] = identities 
  setup_config['fabric']['endorsement-policy']['policy']['1-of'] = policy
  
  with open(os.path.join(new_dir, 'setup.json'), 'w') as f:
    json.dump(setup_config, f, indent=2, sort_keys=True)
  

# Step 5: Update node address in a file
  with open(os.path.join(new_dir, 'nodes.txt'), 'w') as f:
    for peer_node in peer_nodes:
      f.write(peer_node + "\n") 


if __name__ == "__main__":
  main()
