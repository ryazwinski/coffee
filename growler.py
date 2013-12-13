#!/usr/bin/env python

import redis
import gntp.notifier
import json
import time

while True:
    try:
        r=redis.StrictRedis(host='javamon.int.tucows.com')
        s=r.pubsub()
        s.subscribe('coffee-event')
        for event in s.listen():
            if event.get('type') == 'message':
                d_s = event.get('data')
                data = json.loads(d_s)
                if data.has_key('human'):
                    gntp.notifier.mini(data['human'])
    except redis.exceptions.ConnectionError:
        time.sleep(10)
        pass
