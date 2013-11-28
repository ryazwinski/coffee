#!/usr/bin/env python

from utils import tweet, publish
import sys

sys.argv.pop(0)
if len(sys.argv):
    msg=' '.join(sys.argv)
    tweet(msg)
    publish(str({'human': msg}))

