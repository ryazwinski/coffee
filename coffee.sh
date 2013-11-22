#!/bin/bash

HOME=/home/pi
VENVDIR=${HOME}/.virtualenvs/coffee
BINDIR=${HOME}/coffee

cd $BINDIR
. $VENVDIR/bin/activate
python $BINDIR/coffee.py &
echo $! > /var/run/coffee.pid
