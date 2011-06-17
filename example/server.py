from twisted.internet import reactor
from twisted.python import log

import sys

from simplebb.hub import Hub
from simplebb.builder import FileBuilder

log.startLogging(sys.stdout)

fb = FileBuilder('example/projects')

h = Hub()
h.addBuilder(fb)

h.startServer(h.getPBServerFactory(), 'tcp:9222')
h.startServer(h.getShellServerFactory(), 'tcp:9223')

reactor.run()