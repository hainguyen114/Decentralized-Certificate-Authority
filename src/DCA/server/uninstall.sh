#!/bin/bash
killall multichaind
rm -r -f $HOME/.multichain/chaindemo

cd ~/go/bin
export PATH=$HOME/go/bin:$PATH
./storj-sim network destroy
#echo $HOME
