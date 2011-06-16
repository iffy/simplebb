from twisted.spread import pb
from twisted.internet import endpoints
from twisted.internet import reactor
from zope.interface import implements

from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.report import Emitter
from simplebb.builder import Builder
from simplebb.util import generateId

from twisted.python import log


class RemoteHub:
    """
    I wrap a Hub given over the wire so that you can interact with it
    using the IBuilder, IBuilderHub interface.
    """
    
    implements(IBuilder, IEmitter, IObserver, IBuilderHub)

    uid = None

    name = None


    def __init__(self, original):
        self.original = original


    def build(self, request):
        self.original.callRemote('build', request)
    
    
    def addBuilder(self, builder):
        self.original.callRemote('addBuilder', builder)


    def removeBuilder(self, builder):
        self.original.callRemote('removeBuilder', builder)
    
    
    def removeObserver(self, observer):
        self.original.callRemote('removeObserver', observer)


    def addObserver(self, observer):
        self.original.callRemote('addObserver', observer)


    def buildReceived(self, buildDict):
        self.original.callRemote('buildReceived', buildDict)



class Hub(Builder, Emitter, pb.Root):
    """
    I am a build server instance's central hub.
    """
    
    implements(IBuilder, IEmitter, IObserver, IBuilderHub)
    
    remoteHubFactory = RemoteHub


    def __init__(self):
        Emitter.__init__(self)
        Builder.__init__(self)
        self._builders = []
        self._servers = {}
        self._outgoingConns = {}

    
    def buildReceived(self, buildDict):
        """
        Pass along notifications to by observers.
        """
        self.emit(buildDict)


    def addBuilder(self, builder):
        """
        Register a builder to be notified of buildRequests
        """
        if builder not in self._builders:
            self._builders.append(builder)
            log.msg('addBuilder(%r)' % builder)


    def removeBuilder(self, builder):
        """
        Remove a builder from being notified about buildRequests.
        """
        if builder in self._builders:
            self._builders.remove(builder)
    
    
    def _build(self, request):
        """
        Pass along requests to my builders.
        """
        for builder in self._builders:
            builder.build(request)
    
    
    def remote_build(self, request):
        """
        Just build
        """
        self.build(request)
    
    
    def remote_addBuilder(self, builder):
        """
        Wraps the remote builder in remoteHubFactory and passes it on.
        """
        o = self.remoteHubFactory(builder)
        self.addBuilder(o)
    
    
    def remote_removeBuilder(self, builder):
        """
        Finds the wrapped remote builder and removes it.
        """
        for b in list(self._builders):
            if isinstance(b, self.remoteHubFactory):
                if b.original == builder:
                    self.removeBuilder(b)
    
    
    def getServerFactory(self):
        """
        Return a PBServerFactory for listening for connections.
        """
        return pb.PBServerFactory(self)
    
    
    def startServer(self, description):
        """
        Start a PB Server with the given endpoint description string
        """
        server = endpoints.serverFromString(reactor, description)
        factory = self.getServerFactory()
        
        def getServer(server, description):
            self._servers[description] = server
            return server
        return server.listen(factory).addCallback(getServer, description)
    
    
    def stopServer(self, description):
        """
        Stop the server running with the description
        
        @see: U{http://socuteurl.com/tuffyfluffmonsters}
        """
        d = self._servers[description].stopListening()
        del self._servers[description]
        return d
    
    
    def connect(self, description):
        """
        Connect to another PB Server as a client with the given endpoint
        description string
        
        @see: U{http://socuteurl.com/twiggykitteh}
        """
        client = endpoints.clientFromString(reactor, description)
        factory = pb.PBClientFactory()
        
        def getClient(client, description):
            self._outgoingConns[description] = client
            return client
        
        def getRoot(client, factory):
            return factory.getRootObject()
            
        d = client.connect(factory)
        d.addCallback(getClient, description)
        d.addCallback(getRoot, factory)
        d.addCallback(self.gotRemoteRoot)
        return d
    
    
    def disconnect(self, description):
        """
        Disconnect the previous connection (initiated by me) to another
        server matching the given endpoint description.
        """
        d = self._outgoingConns[description].transport.loseConnection()
        del self._outgoingConns[description]
        return d
    
    
    def gotRemoteRoot(self, remote):
        """
        Called when a remote root is received.
        """
        log.msg('got remote root: %s' % remote)
        wrapped = self.remoteHubFactory(remote)
        self.addBuilder(wrapped)
        wrapped.addBuilder(self)
        return wrapped





