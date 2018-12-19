pragma solidity ^0.4.0;
pragma experimental ABIEncoderV2;
contract ycsb {

  mapping(string=>string) store;

  function get(string key) constant returns(string) {
    return store[key];
  }
  function set(string key, string value) {
    store[key] = value;
  }
  function insert(string key, string value) {
    store[key] = value;
  }
  function update(string key, string value) {
    store[key] = value;
  }
  function remove(string key, string value) {
    delete store[key];
  }
  function readmodifywrite(string key, string value) {
    string old_val = store[key];
    store[key] = value;
  }
  function upper(uint num, string[] keys) {
    for (uint i=0; i<num; i++) {
      // string key = keys[i];
      store[keys[i]] = store[keys[i]];
    }
  }
//  function upper(uint num, string key1, string key2, string key3) {
//    store[key1] = store[key1];
//    store[key2] = store[key2];
//    store[key3] = store[key3];
//  }
//  function upper(uint num, string key1, string key2, string key3, 
//                  string key4, string key5) {
//    store[key1] = store[key1];
//    store[key2] = store[key2];
//    store[key3] = store[key3];
//    store[key4] = store[key4];
//    store[key5] = store[key5];
//  }
//  function upper(uint num, string key1, string key2, string key3, 
//                  string key4, string key5, string key6, 
//                  string key7) {
//    store[key1] = store[key1];
//    store[key2] = store[key2];
//    store[key3] = store[key3];
//    store[key4] = store[key4];
//    store[key5] = store[key5];
//    store[key6] = store[key6];
//    store[key7] = store[key7];
//  }
//  function upper(uint num, string key1, string key2, string key3, 
//                  string key4, string key5, string key6, 
//                  string key7, string key8, string key9) {
//    store[key1] = store[key1];
//    store[key2] = store[key2];
//    store[key3] = store[key3];
//    store[key4] = store[key4];
//    store[key5] = store[key5];
//    store[key6] = store[key6];
//    store[key7] = store[key7];
//    store[key8] = store[key8];
//    store[key9] = store[key9];
//  }
}
