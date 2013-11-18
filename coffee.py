__author__ = 'rick'

import bottle
from bottle.ext import sqlite
import datetime

app = bottle.Bottle()
plugin = sqlite.Plugin(dbfile='/Users/rick/coffee/coffee.db')
app.install(plugin)

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

def json_return(status_code, msg):
    import json
    from bottle import response

    response.content_type='application/json'
    response.status = status_code

    return json.dumps(msg)

@app.route('/last')
def last(db):
    row = db.execute('select dts, coffee from raw_log order by dts desc').fetchone()
    if row:
        return json_return(200, "%s: %s" % (row['dts'], row['coffee']))

    return json_return(404, "No rows")

def estimate_complete(dts):
    td = datetime.timedelta(seconds=300)
    return dts+td

@app.route('/brew/:coffee_type')
def brew(coffee_type, db):
    if bottle.request.headers.environ.get('REMOTE_ADDR') != '127.0.0.1':
        return json_return(403, "Can only start a brew from the monitor host - sorry.")

    data = db.execute('select id from coffees')
    coffee_types = [ row['id'] for row in data ]

    if int(coffee_type) not in coffee_types:
        return json_return(403, "Invalid coffee type.")

    row = db.execute('select dts, coffee from raw_log order by dts desc').fetchone()
    now = datetime.datetime.now()

    if row:
        dt = datetime.datetime.strptime(row['dts'], '%Y-%m-%d %H:%M:%S')
        delta = now-dt

        if delta.seconds < 300:
            if coffee_type != str(row['coffee']):
                db.execute('update raw_log set coffee=%s where dts="%s"' % (coffee_type, row['dts']))
                return json_return(200, "brew type changed. Estimated completion: %s" % estimate_complete(dt))
            else:
                return json_return(200, "brew already in progress. Estimated completion: %s" % estimate_complete(dt))

    db.execute('insert into raw_log (coffee) values (?)', coffee_type)
    ret_str = "brew started. Estimated completion: %s" % estimate_complete(now)
    tweet(ret_str)
    return json_return(200, ret_str)

@app.route('/scatter')
def scatter(db):
    import datetime
    data = db.execute('select dts, coffee from raw_log')
    scatter_data = {k: [[0 for i in range(12)] for j in range(24)] for k in range(3)}
    for row in data:
        dt = datetime.datetime.strptime(row['dts'], '%Y-%m-%d %H:%M:%S')
        scatter_data[row['coffee']][dt.hour][dt.minute/5] += 1

    return json_return(200, scatter_data)

@app.route('/favourites')
def favourites(db):
    data = db.execute('select coffee, count(coffee) from raw_log group by coffee;')
    ret = [(row['coffee'], row['count(coffee)']) for row in data]
    return json_return(200, str(ret))

@app.route('/coffees')
def coffees(db):
    data = db.execute('select id, name from coffees')
    ret = [(row['id'], row['name']) for row in data]
    return json_return(200, str(ret))

app.run(host='0.0.0.0', port=8080, debug=True)
