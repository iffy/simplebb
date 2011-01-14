from twisted.protocols import amp
from twisted.internet.protocol import Factory
from simplebb.commands import SendResult, SuggestBuild, Identify, SendStatus
from twisted.python import log


class BuildServer(amp.AMP):
    
    name = 'unknown'
    noisy = False

    def connectionLost(self, reason):
        self.factory.removeBuilder(self)
        return amp.AMP.connectionLost(self, reason)

    def acceptResult(self, projectName, revision, specs, returnCode):
        if returnCode:
            log.msg('FAILED %s %s %s %s' % (returnCode, projectName, revision, self.name))
        else:
            log.msg('SUCCESS %s %s %s' % (projectName, revision, self.name))
        self.factory.sendStatusToClients(projectName, revision, self.name, returnCode)
        return {}
    SendResult.responder(acceptResult)
    
    def acceptBuildSuggestion(self, projectName, revision):
        log.msg('<-- build: %s %s' % (projectName, revision))
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

    def sendStatus(self, projectName, revision, builderName, returnCode):
        d = self.callRemote(SendStatus, projectName=projectName, revision=revision,
                            builderName=builderName, returnCode=returnCode)
        def trapUnhandled(r):
            r.trap(amp.UnhandledCommand)
            return None
        d.addErrback(trapUnhandled)
        return d


class BuildManager(Factory):
    
    protocol = BuildServer
    clients = None
    noisy = False
    
    def __init__(self):
        self.clients = []
    
    def buildProtocol(self, addr):
        proto = Factory.buildProtocol(self, addr)
        return proto
    
    def addBuilder(self, who):
        print '* Builder connected %s' % (who.name,)
        self.clients.append(who)
    
    def removeBuilder(self, who):
        if who in self.clients:
            print '* Builder disconnected %s' % (who.name,)
            self.clients.remove(who)
    
    def suggestBuildToClients(self, projectName, revision):
        if self.clients:
            log.msg('--> build: %s clients %s %s' % (len(self.clients), projectName, revision))
            for client in self.clients:
                client.suggestBuild(projectName, revision)

    def sendStatusToClients(self, projectName, revision, builderName, returnCode):
        if self.clients:
            log.msg('--> result: %s clients %s %s %s %s' % (len(self.clients),
                    returnCode, projectName, revision, builderName))
            for client in self.clients:
                client.sendStatus(projectName, revision, builderName, returnCode)

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