# Orderer, Kafka and ZK Manual Configuration
##  Change ZK Node
Edit the zk nodes at script/config.py

## Change orderer and kafka nodes
* Update new orderer and kafka addresses in configtx.yaml
* Use configtx cmd to generate genesis block and channel.tx
* Property configure the above addresses and channel artifacts fabric.json
* Update new orderer and kafka addresses in script/config.py
* Uncomment init_kafka() in script/launch.py

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




