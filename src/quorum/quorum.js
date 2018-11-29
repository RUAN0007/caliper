/**
 * Copyright 2017 HUAWEI. All Rights Reserved.
 *
 * SPDX-License-Identifier: Apache-2.0
 *
 * @file, definition of the Quorum class, which implements the caliper's NBI for hyperledger quorum
 */

'use strict';

const fs = require('fs');
const Web3 = require('web3');
const solc = require('solc');
const BlockchainInterface = require('../comm/blockchain-interface.js');
const commUtils = require('../comm/util');
const TxStatus = require('../comm/transaction');

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
        return Promise.reject("Not Implemented it");
    }

    unRegisterBlockProcessing() {
        return Promise.reject("Not Implemented it");
    }


    /**
     * Deploy the chaincode specified in the network configuration file to all peers.
     * @return {Promise} The return promise.
     */
    installSmartContract(contracts_config) {
	    return new Promise((resolve, reject) => {
            // Assume there is only one contract
            let contract_config = contracts_config[0];
            let contract_name = contract_config.name;
            let contract_path = commUtils.resolvePath(contract_config.path);

            // Use the first node
            const nodeUrl = this.nodes_info[0].url;
            const web3 = new Web3(new Web3.providers.HttpProvider(nodeUrl));
            if (!web3.isConnected()) {
                reject(new Error("Fail to connect to endpoint " + nodeUrl));
            }
            // compute the abi, bytecode using solc.
            const input = fs.readFileSync(contract_path);
            const output = solc.compile(input.toString(), 1); // convert buffer to string and compile
            const bytecode = '0x' + output.contracts[':' + contract_name].bytecode;
            const abi = JSON.parse(output.contracts[':' + contract_name].interface); // parse ABI
            const contractInstance =  web3.eth.contract(abi);
            contractInstance.new([], {
                from: web3.eth.accounts[0],
                data: bytecode,
                gas: 0x47b760, // Minimum gas to deploy contracts
                privateFor: (this.private ? this.privateFor : undefined)
            }, (err, contract) => {
                if (err) {
                    commUtils.log('err creating contract' + contract_name + err);
                    reject(err);
                } else {
                    if (contract.address) {
                        commUtils.log('Contract mined! Address: ' + contract.address);
                        reject(new Error("Successfully mined the quorum contract"));
                        // resolve([contract.address, abi]);
                    } else {
                        commUtils.log('Contract transaction send: TransactionHash: ' + contract.transactionHash + ' waiting to be mined...');
                    }
                }
            }
            );

        }).catch((err) => {
            commUtils.log('quorum.installSmartContract() failed, ' + (err.stack ? err.stack : err));
            return Promise.reject(err);
        });
    }

    /**
     * Return the Quorum context associated with the given callback module name.
     * @param {string} name The name of the callback module as defined in the configuration files.
     * @param {object} args Unused.
     * @return {object} The assembled Quorum context.
     */
    getContext(name, args, clientIdx) {
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
        let promises = [];
        args.forEach((item, index)=>{
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
                if(func) {
                    simpleArgs.splice(0, 0, func);
                }
                promises.push(Promise.resolve());
            }
            catch(err) {
                commUtils.log(err);
                let badResult = new TxStatus('artifact');
                badResult.SetStatusFail();
                promises.push(Promise.resolve(badResult));
            }
        });
        return Promise.all(promises);
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
        // TODO: change string key to general object
        return Promise.resolve();
    }
}
module.exports = Quorum;
