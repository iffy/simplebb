from twisted.spread import pb
from twisted.internet import endpoints
from twisted.internet import reactor
from zope.interface import implements

from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.report import Emitter
from simplebb.builder import Builder
from simplebb.util import generateId



class Hub(Builder, Emitter, pb.Root):
    """
    I am a build server instance's central hub.
    """
    
    implements(IBuilder, IEmitter, IObserver, IBuilderHub)


    def __init__(self):
        Emitter.__init__(self)
        Builder.__init__(self)
        self._builders = []
        self._servers = {}
        self._clients = {}

    
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
        Wraps the remote builder in remoteBuilderFactory and passes it on.
        """
        o = self.remoteBuilderFactory(builder)
        self.addBuilder(o)
    
    
    def remote_removeBuilder(self, builder):
        """
        Finds the wrapped remote builder and removes it.
        """
        for b in list(self._builders):
            if isinstance(b, self.remoteBuilderFactory):
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
        """
        d = self._servers[description].stopListening()
        del self._servers[description]
        return d
    
    
    def connect(self, description):
        """
        Connect to another PB Server with the given endpoint description string
        """
        client = endpoints.clientFromString(reactor, description)
        factory = pb.PBClientFactory()
        
        def getClient(client, description):
            self._clients[description] = client
            return client
        
        def getRoot(client, factory):
            return factory.getRootObject()
            
        d = client.connect(factory)
        d.addCallback(getClient, description)
        d.addCallback(getRoot, factory)
        d.addCallback(self.gotRemoteRoot)
        return d
    
    
    def disconnect(self, description):
        d = self._clients[description].transport.loseConnection()
        del self._clients[description]
        return d



class RemoteBuilder:
    """
    I wrap a builder given over the wire so that you can interact with it
    using the IBuilder interface.
    """
    
    implements(IBuilder)


    def __init__(self, original):
        self.original = original





