from twisted.internet import reactor, task, utils
from twisted.internet.protocol import ServerFactory
from twisted.application import service, internet

from twisted.python.logfile import LogFile
from twisted.python.log import ILogObserver, FileLogObserver

from simplebb.hub import Hub
from simplebb.builder import FileBuilder

application = service.Application('simplebb')

fb = FileBuilder('example/projects')

h = Hub()
h.addBuilder(fb)


#------------------------------------------------------------------------------
# logging
#------------------------------------------------------------------------------
rotateLength = 1000000
maxRotatedFiles = 5

logfile = LogFile.fromFullPath("server.log", rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)

service.IProcess(application).processName = "simplebb_server"

h.startServer('tcp:9222')
