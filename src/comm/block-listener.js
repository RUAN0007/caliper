const Blockchain = require('./blockchain.js');

const kafka = require('kafka-node');

let kfk_client;
let kfk_producer;
let blockchain;

process.on('message', function(msg) {
    let kafka_config = msg.kfk_config;
    let absNetworkFile = msg.absNetworkFile;

    let broker_urls = kafka_config.broker_urls;
    let topic = kafka_config.topic;
    console.log("Creating the kafka client...");

    kfk_client = new kafka.KafkaClient({kafkaHost: broker_urls});
    blockchain = new Blockchain(absNetworkFile, kafka_config);

    kfk_producer = new kafka.Producer(kfk_client, { requireAcks: -1 })
    kfk_producer.on('error', function (err) {
        console.log("Error from kafka producer...", err);
    });
    

    kfk_producer.on('ready', function () {
        // console.log("Creating the kafka topic..");
        kfk_producer.createTopics([topic], false, function (err, data) {
            if (err) {
                console.log("Error when creating kafka topics...", err);
            } else {
                console.log("Registering for the new block...");
                blockchain.registerNewBlock(kfk_producer)
            }
        })
    });
})

process.on('SIGINT', () => { 
    blockchain.unRegisterNewBlock();
    kfk_producer.close();
    kfk_client.close();
    console.log("Close the kafka client. ");
});
