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
    log.msg(h._builders)
    log.msg(h._clients)
    log.msg(h._servers)
t = task.LoopingCall(monitor)
t.start(5)

reactor.run()