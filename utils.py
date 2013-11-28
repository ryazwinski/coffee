__author__ = 'rick'

from settings import TWEET, PUBLISH, REDIS_HOST, PUBLISH_CHANNEL

def tweet(msg):
    if not TWEET:
        return

    try:
        import twitter
        from twitter_keys import TOKEN, TOKEN_KEY, CON_SEC, CON_SEC_KEY

        my_auth = twitter.OAuth(TOKEN,TOKEN_KEY,CON_SEC,CON_SEC_KEY)
        twit = twitter.Twitter(auth=my_auth)

        twit.statuses.update(status=msg)
    except Exception:
        # if we can't tweet (likely because of missing keys)
        # just ignore it and move on - not critical
        pass

def publish(msg):
    if not PUBLISH:
        return

    try:
        import redis

        r = redis.StrictRedis(host=REDIS_HOST)
        r.publish(PUBLISH_CHANNEL, msg)
    except Exception:
        # probably should log this but for now we'll just ignore it
        pass
