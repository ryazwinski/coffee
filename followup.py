#!/usr/bin/env python

from utils import tweet, publish
from datetime import datetime
from time import sleep
import json
import sys

try:
    cmd=sys.argv.pop(0)
    delay = int(sys.argv.pop(0))
    coffee = sys.argv.pop(0)
except:
    print 'usage: %s delay coffee' % cmd
    sys.exit(1)

msg = 'A pot of %s is ready for you.' % coffee
sleep(delay)
tweet(msg)
publish(json.dumps(({'type': 'complete', 'coffee': coffee, 'end': datetime.now().strftime("%Y%m%d%H%M%S"), 'human': msg})))

