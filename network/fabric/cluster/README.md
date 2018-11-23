# Orderer, Kafka and ZK Manual Configuration

## Change zk, kafka and orderer nodes in the template
* Update new orderer and kafka addresses in configtx.yaml.template
* Update new orderer, kafka and orderer addresses in config.py
* Uncomment init_kafka() in script/launch.py and run only once for the setup

# Mutl-node Setup
## Prepare materials and artifacts for multi-node setup
NOTE: Each peer belongs to a unique peer. 
```
python script/prepare.py <path/to/config> <peer1_addr> <peer2_addr> ...
```

## Start the cluster
python script/launch.py <path/to/config>/setup.json up

## End the cluster
python script/launch.py <path/to/config>/setup.json down

## TO benchmark
* Start the cluster <Prepare first if not prepared>
* cd <path/to/benchmark>, e.g, benchmark/ycsb
* Run the cmd
```
node main.js -n <path/to/config/dir>/setup.json
```
* End the cluster




