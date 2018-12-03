pragma solidity ^0.4.0;

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
}
