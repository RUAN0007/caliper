# Orderer, Kafka and ZK Manual Configuration
##  Change ZK Node
Edit the zk nodes at script/config.py

## Change orderer and kafka nodes
* Update new orderer and kafka addresses in configtx.yaml
* Use configtx cmd to generate genesis block and channel.tx
* Property configure the above addresses and channel artifacts fabric.json
* Update new orderer and kafka addresses in script/config.py
