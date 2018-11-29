pragma solidity ^0.4.0;

contract ycsb {

  mapping(string=>string) store;

  function get(string key) constant returns(string) {
    return store[key];
  }
  function set(string key, string value) {
    store[key] = value;
  }
}
