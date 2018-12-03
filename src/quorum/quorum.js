/**
 * Copyright 2017 HUAWEI. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * @file, definition of the Quorum class, which implements the caliper's NBI for hyperledger quorum
 */

'use strict';

const TxStatus  = require('../comm/transaction');
const fs = require('fs');
const Web3 = require('web3');
const solc = require('solc');
const BlockchainInterface = require('../comm/blockchain-interface.js');
const commUtils = require('../comm/util');

/**
 * Implements {BlockchainInterface} for a Quorum backend.
 */
class Quorum extends BlockchainInterface{
    /**
     * Create a new instance of the {Quorum} class.
     * @param {string} config_path The path of the Quorum network configuration file.
     */
    constructor(config_path) {
        super(config_path);
        let quorum_setup = require(commUtils.resolvePath(config_path));
        // An array of obj {'url': <node_endpoint>, 'pub_key': <node_pub_key>}
        this.nodes_info = quorum_setup.quorum.network;
        if (quorum_setup.quorum.private === 1) {
            this.private = true;
            // Private to every node by default
            this.privateFor = [];
            this.nodes_info.forEach(node_info => {
                this.privateFor.push(node_info.pub_key);
            });
            // console.log("PrivateFor: ", this.privateFor);
        } else {
            console.log("Not Private...");
            this.private = false;
        }
    }

    /**
     * Initialize the {Quorum} object.
     * @return {Promise} The return promise.
     */
    init() {
        // donothing
        return Promise.resolve();
    }

    registerBlockProcessing(clientIdx, callback) {
        console.log("Do nothing registration...");
        // return Promise.resolve();
    }

    unRegisterBlockProcessing() {
        // return Promise.resolve();
    }


    /**
     * Deploy the chaincode specified in the network configuration file to all peers.
     * @return {Promise} The return promise.
     */
    installSmartContract(contracts_config) {
        let bc = this;
        let contract_config = contracts_config[0];
        let contract_name = contract_config.name;
        let contract_path = commUtils.resolvePath(contract_config.path);

        // Use the first node
        const nodeUrl = this.nodes_info[0].url;
        const web3 = new Web3(new Web3.providers.HttpProvider(nodeUrl));
        // compute the abi, bytecode using solc.
        const input = fs.readFileSync(contract_path);
        const output = solc.compile(input.toString(), 1); // convert buffer to string and compile
        const bytecode = '0x' + output.contracts[':' + contract_name].bytecode;
        const abi = JSON.parse(output.contracts[':' + contract_name].interface);
        // console.log("Generated ABI: ", abi_str);

        return web3.eth.getAccounts()
            .then((accounts)=>{
                let from_acc = accounts[0];
                let contractInstance = new web3.eth.Contract(abi);
                return  new Promise((resolve, reject) => {
                    contractInstance.deploy({
                        data: bytecode
                    }).send({
                        from: from_acc,
                        gas: 1500000,
                        privateFor: bc.private? bc.privateFor:undefined
                    }).once('receipt', function(receipt){
                        let addr = receipt.contractAddress.toString();
                        console.log("Receive contract addr in txn receipt ", addr);

                        return resolve([addr, abi]);
                    });
                });
                
        });
    }

    /**
     * Return the Quorum context associated with the given callback module name.
     * @param {string} name The name of the callback module as defined in the configuration files.
     * @param {object} args Unused.
     * @return {object} The assembled Quorum context.
     */
    getContext(name, args, clientIdx) {
        // return Promise.resolve();
        let self = this;
        return new Promise((resolve, reject)=>{
            let web3s = [];
            let my_web3; // endpoint to issue txn

            self.nodes_info.forEach((node_info, idx)=> {

                let node_url = node_info.url;
                const web3 = new Web3(new Web3.providers.HttpProvider(node_url));

                if (clientIdx % this.nodes_info.length === idx) {
                    // console.log("Issued URL: ", node_url);
                    my_web3 = web3; 
                }
                web3s.push(web3); 
            });

            resolve({web3s: web3s, my_web3: my_web3});
        });
    }

    sendTxn(contractInstance, funcName, args, from_acc) {
        let self = this;
        return new Promise((resolve, reject) => {
            // console.log("Issued txn with function ", functionName, " and args ", args[0], args[1]);
            // let before = Date.now();
            contractInstance.methods[funcName](
                ...args
            ).send({
                from: from_acc,
                gas: 1500000,
                privateFor: self.private? self.privateFor:undefined
            }).once('transactionHash', function(hash){
                let txStatus = new TxStatus(hash);

                txStatus.Set('time_commit()', Date.now());
                txStatus.SetStatusSuccess();
                txStatus.SetVerification(true);

                resolve(txStatus);
            });
        });
    }

    /**
     * Release the given Quorum context.
     * @param {object} context The Quorum context to release.
     * @return {Promise} The return promise.
     */
    releaseContext(context) {
        return Promise.resolve();
    }


    /**
     * Invoke the given chaincode according to the specified options. Multiple transactions will be generated according to the length of args.
     * @param {object} context The Quorum context returned by {getContext}.
     * @param {string} contractID The name of the chaincode.
     * @param {string} contractVer The version of the chaincode.
     * @param {Array} args Array of JSON formatted arguments for transaction(s). Each element containts arguments (including the function name) passing to the chaincode. JSON attribute named transaction_type is used by default to specify the function name. If the attribute does not exist, the first attribute will be used as the function name.
     * @param {number} timeout The timeout to set for the execution in seconds.
     * @return {Promise<object>} The promise for the result of the execution.
     */
    invokeSmartContract(context, contractID, contractVer, args, timeout) {
        const web3 = context.my_web3;
        // let node_url = this.nodes_info[context.clientIdx % this.nodes_info.length].url;
        // const web3 = new Web3(new Web3.providers.HttpProvider(node_url));
        let address = contractID[0];
        let abi = contractID[1];

        // let contractInstance = web3.eth.contract(abi).at(address);
        let contractInstance = new web3.eth.Contract(abi, address);
        let self = this;

        return web3.eth.getAccounts()
            .then((accounts)=>{
                let promises = [];
                let from_acc = accounts[0];
                args.forEach((item, index)=>{
                    // let bef = Date.now();
                    try {
                        let simpleArgs = [];
                        let func;
                        for(let key in item) {
                            if(key === 'transaction_type') {
                                func = item[key].toString();
                            }
                            else {
                                simpleArgs.push(item[key].toString());
                            }
                        }
                        promises.push(self.sendTxn(contractInstance, func, simpleArgs, from_acc));
                    } catch(err) {
                        let badResult = new TxStatus('artifact');
                        badResult.SetStatusFail();
                        badResult.SetVerification(true);
                        promises.push(Promise.resolve(badResult));
                    }
                });
                return Promise.all(promises);
            });
    }

    /**
     * Query the given chaincode according to the specified options.
     * @param {object} context The Quorum context returned by {getContext}.
     * @param {string} contractID The name of the chaincode.
     * @param {string} contractVer The version of the chaincode.
     * @param {string} key The argument to pass to the chaincode query.
     * @return {Promise<object>} The promise for the result of the execution.
     */
    queryState(context, contractID, contractVer, key) {
        let address = contractID[0];
        let abi = contractID[1];

        let promises = [];
        let self = this;
        let func = "get";  // Assume each quorum contract has a function named as 'get'
        let txStatus = new TxStatus("00000000000");

        context.web3s.forEach((web3, idx)=>{
            let query_promise = web3.eth.getAccounts().then((accounts)=>{
                let from_acc = accounts[0];
                let contractInstance = new web3.eth.Contract(abi, address);
                let endpoint = self.nodes_info[idx].url;

                return contractInstance.methods[func](key).call({from: from_acc});
            });
                // return self.callMethod(contractInstance, func, [key], from_acc, endpoint); });

            promises.push(query_promise);
        });
        // console.log("Promise len: ", promises.length);
        // Resolve only all nodes reply
        return Promise.all(promises).then((results)=>{
            txStatus.SetStatusSuccess();
            txStatus.SetResult(results[0]);
            // console.log("Query Result: ", results[0]);
            txStatus.SetVerification(true);
            return Promise.resolve(txStatus);
        }).catch( (err) => {
            commUtils.log("Fail to query on key ", key);
            return Promise.reject(err);
        });
    }
}
module.exports = Quorum;
