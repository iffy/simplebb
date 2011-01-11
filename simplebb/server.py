from twisted.protocols import amp
from twisted.internet.protocol import Factory
from simplebb.commands import SendResult, SuggestBuild, Identify
from twisted.python import log


class BuildServer(amp.AMP):
    
    name = 'unknown'

    def connectionLost(self, reason):
        self.factory.removeBuilder(self)
        return amp.AMP.connectionLost(self, reason)

    def acceptResult(self, projectName, revision, specs, returnCode):
        if returnCode:
            log.msg('FAILED %s %s %s %s' % (returnCode, projectName, revision, self.name))
        else:
            log.msg('SUCCESS %s %s %s' % (projectName, revision, self.name))
        return {}
    SendResult.responder(acceptResult)
    
    def acceptBuildSuggestion(self, projectName, revision):
        log.msg('build suggestion received: %s %s' % (projectName, revision))
        self.factory.suggestBuildToClients(projectName, revision)
        return {}
    SuggestBuild.responder(acceptBuildSuggestion)

    def acceptIdentification(self, kind, name):
        self.name = name
        if kind == 'builder':
            self.factory.addBuilder(self)
        return {}
    Identify.responder(acceptIdentification)

    def suggestBuild(self, projectName, revision):
        d = self.callRemote(SuggestBuild, projectName=projectName, revision=revision)
        return d

class BuildManager(Factory):
    
    protocol = BuildServer
    clients = None
    
    def __init__(self):
        self.clients = []
    
    def buildProtocol(self, addr):
        proto = Factory.buildProtocol(self, addr)
        return proto
    
    def addBuilder(self, who):
        print 'Builder connected %s %s' % (who.name, who.transport.getHost().host)
        self.clients.append(who)
    
    def removeBuilder(self, who):
        if who in self.clients:
            print 'Builder disconnected %s %s' % (who.name, who.transport.getPeer().host)
            self.clients.remove(who)
    
    def suggestBuildToClients(self, projectName, revision):
        if self.clients:
            log.msg('Suggesting build of %s %s to %s clients' % (projectName, revision, len(self.clients)))
            for client in self.clients:
                client.suggestBuild(projectName, revision)


def main(port=7900, use_tac=False):
    from twisted.internet import reactor
    from twisted.application.internet import TCPServer
    pf = BuildManager()
    if use_tac:
        return TCPServer(port, pf)
    else:
        reactor.listenTCP(port, pf)
        log.msg('started on port %s' % port)
        reactor.run()


if __name__ == '__main__':
    import sys
    log.startLogging(sys.stdout)
    main()