* number of initial records must be divisble by the total number of clients.
Otherwise, some record may be missing and Fabric will report an error if the queried record is not found. 
*. During later transaction, inserted keys are ordered only within a single process, but not globally ordered.

# To Run with Fabric
Start up the kafka and fabric network sequentially
```
python ../../network/kafka/launch.py up; python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/2p/ up;
```

Start up the driver with the network config as the parameters
```
node main.js -n ../../network/fabric/cluster/2p/setup.json
```

End the fabric and kafka network sequentially. 
```
python ../../network/kafka/launch.py down; python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/2p/ down;
```