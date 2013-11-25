__author__ = 'rick'

def tweet(msg):
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
