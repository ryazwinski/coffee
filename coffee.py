__author__ = 'rick'

import bottle
from bottle.ext import sqlite
import datetime
import os
from utils import tweet, publish
from settings import *

app = bottle.Bottle()
plugin = sqlite.Plugin(dbfile=os.path.join(os.path.dirname(__file__),'coffee.db'))
app.install(plugin)

def json_return(status_code, msg):
    import json
    from bottle import response

    response.content_type='application/json'
    response.status = status_code

    return json.dumps(msg)

def gen_last(count, db):
    data = db.execute('select dts, name from raw_log as r join coffees as c on c.id=r.coffee order by dts desc')
    rows = 0
    ret_a = []
    for row in data:
        if rows >= count:
            break

        ret_a.append("%s %s" % (row['dts'], row['name']))
        rows += 1
    return ret_a

@app.route('/last/<count:int>')
def last(count, db):
    count = int(count)
    ret_a = gen_last(count, db)

    if len(ret_a) > 0:
        return json_return(200, ret_a)

    return json_return(404, "No rows")

@app.route('/last')
def last(db):
    ret_a = gen_last(1, db)
    if len(ret_a) > 0:
        return json_return(200, ret_a[0])

    return json_return(404, "No rows")

def estimate_complete(dts):
    td = datetime.timedelta(seconds=BREW_TIME)
    return dts+td

@app.route('/brew/<coffee_type:int>')
def brew(coffee_type, db):
    if bottle.request.headers.environ.get('REMOTE_ADDR') != '127.0.0.1':
        return json_return(403, "Can only start a brew from the monitor host - sorry.")

    data = db.execute('select id, name from coffees')
    coffees = { row['id'] : row['name'] for row in data }

    if coffee_type not in coffees.keys():
        return json_return(403, "Invalid coffee type.")

    row = db.execute('select dts, coffee from raw_log order by dts desc').fetchone()
    now = datetime.datetime.now()

    if row:
        dt = datetime.datetime.strptime(row['dts'], '%Y-%m-%d %H:%M:%S')
        delta = now-dt

        if delta.seconds < BREW_TIME:
            if coffee_type != row['coffee']:
                db.execute('update raw_log set coffee=%d where dts="%s"' % (coffee_type, row['dts']))
                return json_return(200, "brew type changed. Estimated completion: %s" % estimate_complete(dt))
            else:
                return json_return(200, "brew already in progress. Estimated completion: %s" % estimate_complete(dt))

    db.execute('insert into raw_log (coffee) values (%d)' % coffee_type)
    eta = estimate_complete(now)
    ret_str = "Brew started: %s. Estimated completion: %s" % (coffees[coffee_type], eta)

    tweet(ret_str)
    publish(str({'human': ret_str, 'type': 'start', 'coffee': coffees[coffee_type], 'start': now, 'estimate': eta}))

    os.system("(%s/followup.sh %d %s)&" %
              (os.path.dirname(__file__), BREW_TIME, coffees[coffee_type]))

    return json_return(200, ret_str)

@app.route('/scatter')
def scatter(db):
    import datetime

    data = db.execute('select id, name from coffees')
    coffees = {row['id']: row['name'] for row in data}
    num_coffees = len(coffees)
    found_coffees = set()

    # [['time', 'house count', 'sumatra count'],
    #  ['0:00', 0, 0],
    #  ['0:05', 1, 0],...]

    scatter_data = {k: [[0 for i in range(60/MINUTE_BIN_SIZE)] for j in range(24)] for k in range(num_coffees)}
    data = db.execute('select dts, coffee from raw_log')

    for row in data:
        dt = datetime.datetime.strptime(row['dts'], '%Y-%m-%d %H:%M:%S')
        scatter_data[row['coffee']][dt.hour][dt.minute/MINUTE_BIN_SIZE] += 1
        found_coffees.add(row['coffee'])

    return_data = []

    line = ['time'] + [ coffees[c] for c in coffees.keys() if c in found_coffees]
    return_data.append(line)

    for hours in range(24):
        for minutes in range(60/MINUTE_BIN_SIZE):
            #line = [ '%d:%02d' % (hours, minutes*5)]
            line = [ [ hours, minutes*MINUTE_BIN_SIZE, 0, 0] ]
            found = False
            for coffee in range(num_coffees):
                if not coffee in found_coffees:
                    continue

                if scatter_data[coffee][hours][minutes] > 0:
                    found = True
                    line.append(scatter_data[coffee][hours][minutes])
                else:
                    line.append(0)

            if found:
                return_data.append(line)

    return json_return(200, return_data)

@app.route('/favourites')
def favourites(db):
    # [['coffee', 'count'],
    #  ['unknown', 10],
    #  ['house', 20],..]

    data = db.execute('select id, name from coffees')
    coffees = {row['id']: row['name'] for row in data}

    data = db.execute('select coffee, count(coffee) from raw_log group by coffee;')
    ret = [[row['coffee'], row['count(coffee)']] for row in data]
    for row in ret:
        row[0] = str(coffees[row[0]])

    ret.insert(0,['coffee', 'count'])
    return json_return(200, str(ret))

@app.route('/dow')
def dow(db):
    data = db.execute('''
        select day_of_week, count(day_of_week) from (
            select strftime("%w", date(distinct_date)) as day_of_week from (
                        select distinct strftime("%Y-%m-%d", dts) as distinct_date from raw_log
                            )
            )
        group by day_of_week;'''
    );
    count_of_weekdays_logged = { int(row['day_of_week']): int(row['count(day_of_week)']) for row in data }

    data = db.execute('''
        select day_of_week, count(day_of_week) from (
            select strftime("%w", dts) as day_of_week from raw_log
        ) group by day_of_week;'''
    );
    raw_brews_by_weekday = { int(row['day_of_week']): int(row['count(day_of_week)']) for row in data }

    average_brews_by_weekday = [ 0 for x in range(7) ]
    for day in raw_brews_by_weekday.keys():
        average_brews_by_weekday[day] = raw_brews_by_weekday[day]/count_of_weekdays_logged[day]

    days = ['Sun','Mon','Tues','Wed','Thurs','Fri','Sat']
    return_array = [['Day', 'Count']]
    for day in range(7):
        return_array.append([days[day], average_brews_by_weekday[day]])

    return json_return(200, str(return_array))




@app.route('/coffees')
def coffees(db):
    data = db.execute('select id, name from coffees')
    ret = [(row['id'], row['name']) for row in data]
    return json_return(200, str(ret))

@app.route('/')
@app.route('/<unknown>')
def index(unknown='ignored'):
    import os
    return bottle.static_file('index.html', root=os.path.dirname(__file__))

app.run(server='paste', host='0.0.0.0', port=8080, debug=False, quiet=True)
