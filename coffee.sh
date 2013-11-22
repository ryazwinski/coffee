#!/bin/bash

HOME=~
VENVDIR=$HOME/.virtualenvs/coffee
BINDIR=$HOME/coffee

cd $BINDIR
source $VENVDIR/bin/activate
python $BINDIR/coffee.py
echo $! > /var/run/coffee.pid
