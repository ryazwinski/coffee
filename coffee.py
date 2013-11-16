__author__ = 'rick'

import bottle
from bottle.ext import sqlite
import datetime

app = bottle.Bottle()
plugin = sqlite.Plugin(dbfile='/Users/rick/coffee/coffee.db')
app.install(plugin)

@app.route('/last')
def last(db):
    row = db.execute('select dts, coffee from raw_log order by dts desc').fetchone()
    if row:
        return "%s: %s" % (row['dts'], row['coffee'])

    return "No rows"

def estimate_complete(dts):
    td = datetime.timedelta(seconds=300)
    return dts+td

@app.route('/brew/:type')
def brew(type, db):
    if bottle.request.headers.environ.get('REMOTE_ADDR') != '127.0.0.1':
        return "Can only start a brew from the monitor host - sorry."

    row = db.execute('select dts, coffee from raw_log order by dts desc').fetchone()
    now = datetime.datetime.utcnow()

    if row:
        dt = datetime.datetime.strptime(row['dts'], '%Y-%m-%d %H:%M:%S')
        delta = now-dt

        if delta.seconds < 300:
            if type != str(row['coffee']):
                db.execute('update raw_log set coffee=%s where dts="%s"' % (type, row['dts']))
                return "brew type changed. Estimated completion: %s" % estimate_complete(dt)
            else:
                return "brew already in progress. Estimated completion: %s" % estimate_complete(dt)

    db.execute('insert into raw_log (dts, coffee) values (CURRENT_TIMESTAMP, ?)', type)
    return "brew started. Estimated completion: %s" % estimate_complete(now)

@app.route('/scatter')
def scatter(db):
    import datetime
    data = db.execute('select dts, coffee from raw_log')
    scatter_data = [[[0,0,0] for i in range(12)] for j in range(24)]
    for row in data:
        print row['dts'], row['coffee']
        dt = datetime.datetime.strptime(row['dts'], '%Y-%m-%d %H:%M:%S')
        scatter_data[dt.hour][dt.minute/5][row['coffee']] += 1

    return str(scatter_data)

@app.route('/favourites')
def favourites(db):
    data = db.execute('select coffee, count(coffee) from raw_log group by coffee;')
    ret = [(row['coffee'], row['count(coffee)']) for row in data]
    return str(ret)

@app.route('/coffees')
def coffees(db):
    data = db.execute('select id, name from coffees')
    ret = [(row['id'], row['name']) for row in data]
    return str(ret)

app.run(host='localhost', port=8080, debug=True)