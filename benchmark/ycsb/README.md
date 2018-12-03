# NOTE: 
* number of initial records must be divisble by the total number of clients.
Otherwise, some record may be missing and Fabric will report an error if the queried record is not found. 
*. During later transaction, inserted keys are ordered only within a single process, but not globally ordered.

# To Run with Fabric
Start up the network
```
 python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/2p/ up;
```

Start up the driver with the network config
```
node main.js -c fabric-config.json -n ../../network/fabric/cluster/env/2p/setup.json
```

Shut down the network. 
```
python ../../network/fabric/cluster/script/launch.py ../../network/fabric/cluster/env/2p/ down;
```

# To Run with Quorum
Start up the network
```
../../network/quorum/init-all.sh <#-of-nodes> [-p]; # permissioned with -p
../../network/quorum/start-all.sh <#-of-nodes> [-p]; 
```

Start up the driver with the network config
```
node main.js -c quorum-config.json -n ../../network/quorum/qdata/setup.json
```


Shut down the network. 
```
../../network/quorum/stop-all.sh <#-of-nodes>
```
