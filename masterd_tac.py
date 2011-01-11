from twisted.protocols.amp import AMP, Command, Integer, String
from twisted.python.usage import Options, UsageError
from twisted.internet import reactor, task, utils
from twisted.internet.protocol import ServerFactory
import sys,re
from twisted.application import service, internet
from simplebb.server import main

rotateLength = 1000000
maxRotatedFiles = 5

from twisted.python.logfile import LogFile
from twisted.python.log import ILogObserver, FileLogObserver

application = service.Application("My app")
logfile = LogFile.fromFullPath("server.log", rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)



service.IProcess(application).processName = "simplebbsd"
s = main(use_tac=True)
s.setServiceParent(application)
