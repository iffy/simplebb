#!/usr/bin/python

from twisted.internet import task
from twisted.python import log
from twisted.internet import reactor
import sys

log.startLogging(sys.stdout)

from simplebb.hub import Hub

h = Hub()
h.startServer('tcp:8100')

def monitor():
    txt = 'builders: %s, outgoing: %s, servers: %s' % (
        len(h._builders), len(h._outgoingConns), len(h._servers))
    log.msg(txt)
t = task.LoopingCall(monitor)
t.start(5)

reactor.run()