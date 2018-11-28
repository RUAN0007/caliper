eth.getTransaction("0xbab0e080e9b236f03f5095ab268c08700547652d93207fc063109908ee611141")
eth.getReceipt("0xbab0e080e9b236f03f5095ab268c08700547652d93207fc063109908ee611141")

var address = "0x6c08bfc519c47659176ffa46d78b7e3c380ee94f";

var abi = [{"constant":true,"inputs":[],"name":"storedData","outputs":[{"name":"","type":"uint256"}],"payable":false,"type":"function"},{"constant":false,"inputs":[{"name":"x","type":"uint256"}],"name":"set","outputs":[],"payable":false,"type":"function"},{"constant":true,"inputs":[],"name":"get","outputs":[{"name":"retVal","type":"uint256"}],"payable":false,"type":"function"},{"inputs":[{"name":"initVal","type":"uint256"}],"type":"constructor"}];
var private = eth.contract(abi).at(address);
private.get()
private.set(14,{from:eth.coinbase,privateFor:["i0tSntO46ZV3ggoWD0yEW3mDhrPsZFQut8R+lZmJwkc="]});

