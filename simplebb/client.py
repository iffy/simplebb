from twisted.protocols import amp
from simplebb.commands import SendResult, SuggestBuild, Identify, SendStatus
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, utils, defer
from twisted.python.filepath import FilePath
import os
import sys

from twisted.python import log

buildscriptdir = FilePath(os.environ['HOME']).child('.simplebb').child('buildscripts')
statusFileLogObserver = None

class ClientProto(amp.AMP):
    
    statusData = None
    
    def connectionMade(self):
        self.statusData = {}
        amp.AMP.connectionMade(self)
        self.callRemote(Identify, kind='builder', name=self.factory.name)

    def acceptBuildSuggestion(self, projectName, revision):
        print '<-- build: %s %s' % (projectName, revision)
        self.factory.buildProject(projectName, revision)
        return {}
    SuggestBuild.responder(acceptBuildSuggestion)
    
    @SendStatus.responder
    def acceptStatus(self, projectName, revision, builderName, returnCode):
        global statusFileLogObserver
        #print '<-- status: %s %s %s %s' % (returnCode, projectName, revision, builderName)
        if projectName not in self.statusData:
            self.statusData[projectName] = {}
        projectStatus = self.statusData[projectName]
        if revision not in projectStatus:
            projectStatus[revision] = []
        projectStatus[revision].append((returnCode, builderName))
        
        passfail = 'FAILED'
        if not returnCode:
            passfail = 'PASSED'
        logmsg = '%s %4s %s/%s "%s"' % (
                    passfail,
                    returnCode,
                    projectName,
                    revision,
                    builderName,
                )
        log.msg(logmsg, isBuildReport=True)
        return {}


class MyClient(ClientFactory):  
    conn = None
    protocol = ClientProto
    retryInterval = 1.0
    name = os.uname()[1]
    
    def clientConnectionLost(self, connector, reason):
        print '* connection lost'
        self.reconnect(connector)

    def clientConnectionFailed(self, connector, reason):
        print '* connection failed'
        self.reconnect(connector)

    def buildProtocol(self, addr):
        print '* connected to server'
        proto = ClientFactory.buildProtocol(self, addr)
        self.retryInterval = 1
        self.conn = proto
        self.conn.factory = self
        self.specs = self.getSpecs()
        return proto

    def reconnect(self, connector):
        print '* will try to reconnect in %.2fs' % self.retryInterval
        reactor.callLater(self.retryInterval, self._reconnect, connector)
        self.retryInterval = min(self.retryInterval * 1.3, 3600)

    def _reconnect(self, connector):
        connector.connect()

    def sendResult(self, projectName, revision, returnCode):
        print '--> %s %s %s' % (returnCode, projectName, revision)
        return self.conn.callRemote(SendResult, projectName=projectName,
                                    revision=revision, specs=self.specs, returnCode=returnCode)
    def getSpecs(self):
        return ' '.join(os.uname()) + '\n' + sys.version

    def buildProject(self, name, revision):
        """
        Runs the script in the buildscripts dir
        """
        global buildscriptdir
        script = buildscriptdir.child(name)
        d = defer.Deferred()
        if not script.exists():
            print 'Build script does not exist: %s' % script.path
            d.callback((name, revision, -1, 'Build script does not exist'))
        else:
            d = utils.getProcessOutputAndValue(script.path, args=(revision,), env=None)
            def cb(v):
                stdout, stderr, value = v
                return (name, revision, value, stdout + stderr)
            d.addCallback(cb)
        d.addCallback(self._projectBuilt)
        return d
    
    def _projectBuilt(self, result):
        name, revision, returnCode, notes = result
        if returnCode:
            print '='*30
            print 'FAILED', returnCode, name, revision
            print notes
            print '='*30
        else:
            print '-'*30
            print 'SUCCESS', returnCode, name, revision
            print '-'*30
        return self.sendResult(name, revision, returnCode)


def statusLogObserver(d):
    global statusFileLogObserver
    #print 'observer?'
    if statusFileLogObserver and 'isBuildReport' in d:
        statusFileLogObserver.emit(d)

def main(host, mybuildscriptdir=None, name=None, statusLogFile='buildstatus.log', port=7900, use_tac=False):
    global buildscriptdir, statusFileLogObserver
    f = MyClient()
    f.name = name or f.name
    
    # set up the status log
    if statusLogFile:
        statusLogFile = FilePath(statusLogFile)
        statusFileLogObserver = log.FileLogObserver(open(statusLogFile.path, 'a'))
        log.addObserver(statusLogObserver)
    
    # where the build scripts are
    if mybuildscriptdir:
        buildscriptdir = FilePath(mybuildscriptdir)
    
    if use_tac:
        from twisted.application.internet import TCPClient
        return TCPClient(host, port, f)
    else:
        reactor.connectTCP(host, port, f)

if __name__ == '__main__':
    host = sys.argv[1]
    main(host)
    reactor.run()



