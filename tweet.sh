#!/bin/bash

HOME=/home/pi
VENVDIR=${HOME}/.virtualenvs/coffee
BINDIR=${HOME}/coffee

cd $BINDIR
. $VENVDIR/bin/activate
#python $BINDIR/tweet.py $* 
echo $*
