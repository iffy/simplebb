from twisted.internet import reactor, task, utils
from twisted.application import service, internet
from simplebb.client import main

rotateLength = 1000000
maxRotatedFiles = 5

from twisted.python.logfile import LogFile
from twisted.python.log import ILogObserver, FileLogObserver

application = service.Application("My app")
logfile = LogFile.fromFullPath("builder.log", rotateLength=rotateLength,
                                 maxRotatedFiles=maxRotatedFiles)
application.setComponent(ILogObserver, FileLogObserver(logfile).emit)

service.IProcess(application).processName = "simplebbbd"
s = main('127.0.0.1', '~/.simplebb/buildscripts', name='mycomputer (myspecs)', use_tac=True)
s.setServiceParent(application)
