#!/usr/bin/env python

# This is a basic script that will check that
# multithreaded behavior works as expected.
# The idea is to spin up a multithreaded server
# with views that use flask-shelve, and then to
# spawn multi threaded clients.
import os
import time
import threading
from urllib2 import urlopen

from werkzeug.serving import make_server
import flask
from flask.ext import shelve

NUM_CLIENTS = 20
NUM_REQUESTS = 50


app = flask.Flask('test-flask-shelve')
app.debug = True
app.config["SHELVE_FILENAME"] = 'demodb'
shelve.init_app(app)


def make_requests(num_requests):
    for i in xrange(num_requests):
        urlopen('http://localhost:5000/incr/').read()


@app.route('/incr/')
def setkey():
    db = shelve.get_shelve('c')
    if 'counter' not in db:
        db['counter'] = 0
    current = db['counter']
    time.sleep(0.01)
    db['counter'] = current + 1
    return str(db['counter']) + '\n'


@app.route('/count/')
def getkey():
    db = shelve.get_shelve('r')
    time.sleep(0.01)
    return str(db['counter']) + '\n'


@app.route('/reset/')
def reset():
    db = shelve.get_shelve('c')
    time.sleep(0.01)
    db['counter'] = 0
    return '0\n'


if __name__ == '__main__':
    server = make_server('127.0.0.1', 5000, app, threaded=True)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    print "Starting server"
    server_thread.start()
    time.sleep(2)
    clients = []
    for i in xrange(NUM_CLIENTS):
        t = threading.Thread(target=make_requests,
                             kwargs={'num_requests': NUM_REQUESTS})
        clients.append(t)
    urlopen('http://localhost:5000/reset/').read()
    print "Starting clients"
    start = time.time()
    for client in clients:
        client.start()
    for client in clients:
        client.join()
    end = time.time()
    val = int(urlopen('http://localhost:5000/count/').read().strip())
    print "Expected:", NUM_CLIENTS * NUM_REQUESTS
    print "Actual  :", val
    print "Time    : %.2f" % (end - start)
    os.unlink(app.config["SHELVE_FILENAME"])
    os.unlink(app.config["SHELVE_LOCKFILE"])
