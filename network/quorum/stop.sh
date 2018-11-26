#!/bin/bash
cd `dirname ${BASH_SOURCE-$0}`
. env.sh

echo "stop.sh" 
killall -KILL ${QUORUM}
rm -rf $QUO_DATA
rm -rf ~/.eth*