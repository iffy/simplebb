from twisted.internet import reactor, task, utils
from twisted.python import log

import sys

from simplebb.hub import Hub
from simplebb.builder import FileBuilder

log.startLogging(sys.stdout)

fb = FileBuilder('example/projects')

h = Hub()
h.addBuilder(fb)

h.connect('tcp:host=127.0.0.1:port=9222')
h.startServer(h.getShellServerFactory(), 'tcp:9224')

reactor.run()