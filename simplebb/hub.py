from twisted.spread import pb
from twisted.internet import endpoints
from twisted.internet import reactor, defer
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
    
    hub = None


    def __init__(self, original):
        self.original = original
    
    
    def __eq__(self, other):
        if other is self:
            return True
        if isinstance(other, RemoteHub):
            return other.original == self.original
        return False
    
    
    def wrappedCallRemote(self, *args):
        """
        I catch callRemote's exceptions and disconnect myself from the hub
        if the remote side disconnected.
        """
        result = self.original.callRemote(*args)
        return result


    def build(self, request):
        self.wrappedCallRemote('build', request)
    
    
    def addBuilder(self, builder):
        self.wrappedCallRemote('addBuilder', builder)


    def remBuilder(self, builder):
        self.wrappedCallRemote('remBuilder', builder)
    
    
    def remObserver(self, observer):
        self.wrappedCallRemote('remObserver', observer)


    def addObserver(self, observer):
        self.wrappedCallRemote('addObserver', observer)


    def buildReceived(self, buildDict):
        self.wrappedCallRemote('buildReceived', buildDict)



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
        Called by Emitters that I am observing to indicate that something
        interesting has happened with this build.
        """
        self.emit(buildDict)


    def addBuilder(self, builder):
        """
        Register a builder to be notified of buildRequests that I received.
        """
        if builder not in self._builders:
            self._builders.append(builder)


    def remBuilder(self, builder):
        """
        Remove a builder from being notified about buildRequests.
        """
        if builder in self._builders:
            self._builders.remove(builder)
    
    
    def _build(self, request):
        """
        As a Hub, I pass build requests on to my list of Builders.
        """
        for builder in self._builders:
            builder.build(request)

    # ------------------------------------------------------------------------
    # remote methods   
    # ------------------------------------------------------------------------
    
    def remote_build(self, request):
        """
        Call through to build.
        """
        self.build(request)
    
    
    def remote_addBuilder(self, builder):
        """
        Wraps the remote builder in remoteHubFactory and passes it on.
        """
        o = self.remoteHubFactory(builder)
        self.addBuilder(o)
    
    
    def remote_remBuilder(self, builder):
        """
        Finds the wrapped remote builder and removes it.
        """
        o = self.remoteHubFactory(builder)
        self.remBuilder(o)
    
    
    def remote_getUID(self):
        """
        Returns my uid
        """
        return self.uid
    
    
    def remote_getName(self):
        """
        Returns my name
        """
        return self.name
    
    
    def remote_addObserver(self, observer):
        """
        Add the remote observer to my list of observers
        """
        wrapped = self.remoteHubFactory(observer)
        self.addObserver(wrapped)


    def remote_remObserver(self, observer):
        """
        Add the remote observer to my list of observers
        """
        wrapped = self.remoteHubFactory(observer)
        self.remObserver(wrapped)

    # ------------------------------------------------------------------------
    # hub server
    # ------------------------------------------------------------------------
    
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
        Called when a remote root is received as a client.
        
        In otherwords, C{self} is the client connecting to the C{remote} server.
        """
        self.remote_addBuilder(remote)
        self.remote_addObserver(remote)
        remote.callRemote('addBuilder', self)
        remote.callRemote('addObserver', self)





