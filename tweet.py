#!/usr/bin/env python

from twitterhelp import tweet
import sys

sys.argv.pop(0)
if len(sys.argv):
    tweet(' '.join(sys.argv))
