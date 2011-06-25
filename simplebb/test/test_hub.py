from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject

from twisted.internet.endpoints import clientFromString
from twisted.internet import reactor, defer
from twisted.spread import pb

from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.hub import Hub, RemoteHub
from simplebb.builder import Builder
from simplebb.shell import ShellFactory



class FakeReference:
    """
    I fake Remotes
    """

    def __init__(self):
        self.called = []
        self.result = defer.Deferred()

    def callRemote(self, *args):
        self.called.append(args)
        return self.result



class FakeRemoteHub:
    
    def __init__(self, original):
        self.original = original



class HubTest(TestCase):
    
    
    timeout = 1


    def test_IBuilder(self):
        verifyClass(IBuilder, Hub)
        verifyObject(IBuilder, Hub())
    
    
    def test_IEmitter(self):
        verifyClass(IEmitter, Hub)
        verifyObject(IEmitter, Hub())
    
    
    def test_IObserver(self):
        verifyClass(IObserver, Hub)
        verifyObject(IObserver, Hub())

    
    def test_IBuilderHub(self):
        verifyClass(IBuilderHub, Hub)
        verifyObject(IBuilderHub, Hub())
    
    
    def test_Builder(self):
        self.assertTrue(issubclass(Hub, Builder))
    
    
    def test_pbRoot(self):
        """
        Should be able to be shared over the wire
        """
        self.assertTrue(issubclass(Hub, pb.Root))
    
    
    def test_remoteHubFactory(self):
        """
        Should use RemoteHub as the factory
        """
        self.assertEqual(Hub.remoteHubFactory, RemoteHub)
    
    
    def test_noteReceived(self):
        """
        Should just call emit
        """
        h = Hub()
        called = []
        h.emit = called.append
        h.noteReceived('something')
        self.assertEqual(called, ['something'])
    
    
    def test_addBuilder(self):
        """
        Should add builder to _builders list
        """
        h = Hub()
        o = object()
        h.addBuilder(o)
        self.assertEqual(h._builders, [o])
        h.addBuilder(o)
        self.assertEqual(h._builders, [o])


    def test_remBuilder(self):
        """
        Should remove from the _builders list
        """
        h = Hub()
        o = object()
        h._builders = [o]
        h.remBuilder(o)
        self.assertEqual(h._builders, [])
        h.remBuilder(o)
        self.assertEqual(h._builders, [])


    def test__build(self):
        """
        Should pass it along to all registered builders.
        """
        class FakeBuilder:
            def build(self, request):
                self.called = request
        
        b = FakeBuilder()
        h = Hub()
        h.addBuilder(b)
        r = {}
        h._build(r)
        self.assertEqual(b.called, r)


    def test_remote_build(self):
        """
        Should have a remote build that just runs build
        """
        h = Hub()
        called = []
        h.build = called.append
        o = dict(foo='bar')
        h.remote_build(o)
        self.assertEqual(called, [o])
    
    
    def test_remote_addBuilder(self):
        """
        Should wrap the remote in a RemoteHub then call addBuilder
        """
        h = Hub()
        h.remoteHubFactory = FakeRemoteHub
        called = []
        h.addBuilder = called.append
        h.remote_addBuilder('foo')
        
        self.assertEqual(len(called), 1)
        r = called[0]
        self.assertTrue(isinstance(r, FakeRemoteHub))
        self.assertEqual(r.original, 'foo')
        self.assertEqual(r.hub, h)
    
    
    def test_remote_remBuilder(self):
        """
        Should wrap the remote then call remBuilder
        """
        h = Hub()
        h.remoteHubFactory = FakeRemoteHub
        called = []
        h.remBuilder = called.append
        h.remote_remBuilder('foo')
        
        self.assertEqual(len(called), 1)
        r = called[0]
        self.assertTrue(isinstance(r, FakeRemoteHub))
        self.assertEqual(r.original, 'foo')


    def test_remote_getUID(self):
        """
        Should just return uid
        """
        h = Hub()
        h.uid = 'foo'
        self.assertEqual(h.remote_getUID(), 'foo')


    def test_remote_getName(self):
        """
        Should just return the name
        """
        h = Hub()
        h.name = 'name'
        self.assertEqual(h.remote_getName(), 'name')


    def test_remote_addObserver(self):
        """
        Should wrap the remote and call addObserver
        """
        h = Hub()
        h.remoteHubFactory = FakeRemoteHub
        called = []
        h.addObserver = called.append
        
        h.remote_addObserver('foo')
        
        self.assertEqual(len(called), 1)
        observer = called[0]
        self.assertTrue(isinstance(observer, FakeRemoteHub))
        self.assertEqual(observer.original, 'foo')
        self.assertEqual(observer.hub, h)


    def test_remote_remObserver(self):
        """
        Should wrap the remote and call removeObserver
        """
        h = Hub()
        h.remoteHubFactory = FakeRemoteHub
        called = []
        h.remObserver = called.append
        
        h.remote_remObserver('foo')
        
        self.assertEqual(len(called), 1)
        observer = called[0]
        self.assertTrue(isinstance(observer, FakeRemoteHub))
        self.assertEqual(observer.original, 'foo')


    def test_getPBServerFactory(self):
        """
        Should return an instance of pb.PBServerFactory with self passed in.
        """
        h = Hub()
        f = h.getPBServerFactory()
        self.assertTrue(isinstance(f, pb.PBServerFactory))
        self.assertEqual(f.root, h)
    
    
    def test_getShellServerFactory(self):
        """
        Should return an instance of hub.shell.ShellFactory
        """
        h = Hub()
        f = h.getShellServerFactory()
        self.assertTrue(isinstance(f, ShellFactory))
        self.assertEqual(f.hub, h)
    
    
    def test_startServer(self):
        """
        Should call twisted.internet.endpoints.serverFromString and hook that
        up to the factory
        """
        h = Hub()
        h.remote_echo = lambda x: x
        h.startServer(h.getPBServerFactory(), 'tcp:10999')
        
        # connect to it
        self.clientPort = None
        client = clientFromString(reactor, 'tcp:host=127.0.0.1:port=10999')
        factory = pb.PBClientFactory()
        d = client.connect(factory)
        
        def saveClient(clientPort):
            self.clientPort = clientPort

        d.addCallback(saveClient)
        d.addCallback(lambda ign: factory.getRootObject())
        d.addCallback(lambda obj: obj.callRemote('echo', 'foo'))
        d.addCallback(lambda res: self.assertEqual(res, 'foo'))
        d.addCallback(lambda ign: self.clientPort.transport.loseConnection())
        d.addCallback(lambda ign: h.stopServer('tcp:10999'))
        return d


    def test_stopServer(self):
        """
        You can have many servers running and stop them individually
        """
        h = Hub()
        h.remote_echo = lambda x: x
        d = h.startServer(h.getPBServerFactory(), 'tcp:10999')
        d.addCallback(lambda x: h.startServer(h.getPBServerFactory(),
                                              'tcp:10888'))
        
        def killOne(_):
            return h.stopServer('tcp:10888')
        d.addCallback(killOne)
        
        
        def testOne(_):
            # still can connect to the other
            self.clientPort = None
            client = clientFromString(reactor, 'tcp:host=127.0.0.1:port=10999')
            factory = pb.PBClientFactory()
            d = client.connect(factory)
            
            def saveClient(clientPort):
                self.clientPort = clientPort
    
            d.addCallback(saveClient)
            d.addCallback(lambda ign: factory.getRootObject())
            d.addCallback(lambda obj: obj.callRemote('echo', 'foo'))
            d.addCallback(lambda res: self.assertEqual(res, 'foo'))
            d.addCallback(lambda ign: self.clientPort.transport.loseConnection())
            d.addCallback(lambda ign: h.stopServer('tcp:10999'))
            return d
        d.addCallback(testOne)
        return d
    
    
    def test_stopServer_notThere(self):
        """
        It is an error to stop a server that does not exist
        """
        h = Hub()
        self.assertRaises(KeyError, h.stopServer, 'foobar')
    
    
    def test_connect(self):
        """
        You can connect to other servers.  This is functionalish
        """
        server = Hub()
        client = Hub()
        called = []
        client.remoteHubFactory = lambda x: 'foo'
        client.gotRemoteRoot = called.append

        server.startServer(server.getPBServerFactory(), 'tcp:10999')
        
        def check(r):
            self.assertEqual(called, ['foo'],
                "Should have called .gotRemoteRoot with wrapped remote")
            return r
        
        d = client.connect('tcp:host=127.0.0.1:port=10999')
        d.addCallback(check)
        d.addCallback(lambda x: client.disconnect(
                      'tcp:host=127.0.0.1:port=10999'))
        d.addCallback(lambda x: server.stopServer('tcp:10999'))
        return d


    def test_gotRemoteRoot(self):
        """
        Should add remote to builder and observers, add self to remote builders
        and observers, start static info fetching.
        """
        hub = Hub()
        remote = FakeRemoteHub('foo')
        
        called = []
        def makeFake(name):
            def f(*args):
                called.append((name, args))
            return f
        
        hub.addBuilder = makeFake('addB')
        hub.addObserver = makeFake('addO')
        
        remote.addBuilder = makeFake('r_addB')
        remote.addObserver = makeFake('r_addO')
        remote.getStaticInfo = makeFake('r_getStaticInfo')

        hub.gotRemoteRoot(remote)
        
        self.assertEqual(set(called), set([
            ('addB', (remote,)),
            ('addO', (remote,)),
            ('r_addB', (hub,)),
            ('r_addO', (hub,)),
            ('r_getStaticInfo', ()),
        ]))
        self.assertEqual(remote.hub, hub)



class RemoteHubTest(TestCase):

    timeout = 1


    def test_IBuilder(self):
        verifyClass(IBuilder, RemoteHub)
        verifyObject(IBuilder, RemoteHub('foo'))


    def test_IEmitter(self):
        verifyClass(IEmitter, RemoteHub)
        verifyObject(IEmitter, RemoteHub('foo'))
    
    
    def test_IObserver(self):
        verifyClass(IObserver, RemoteHub)
        verifyObject(IObserver, RemoteHub('foo'))
    
    
    def test_IBuilderHub(self):
        verifyClass(IBuilderHub, RemoteHub)
        verifyObject(IBuilderHub, RemoteHub('foo'))


    def test_init(self):
        """
        Requires an object that will be the actual transport mechanism
        """
        b = RemoteHub('foo')
        self.assertEqual(b.original, 'foo')
        self.assertEqual(b.hub, None)
    
    
    def test_getStaticInfo(self):
        """
        Should ask for uid and name
        """
        ref = FakeReference()
        
        def callRemote(cmd):
            return defer.succeed(cmd)    
        ref.callRemote = callRemote

        remote = RemoteHub(ref)        
        remote.getStaticInfo()
        
        self.assertEqual(remote.uid, 'getUID')
        self.assertEqual(remote.name, 'getName')


    def tr(self, meth, *args):
        """
        I test that calling meth calls callRemote(meth, *args)
        """
        b = RemoteHub('foo')
        called = []
        def fake(*args):
            called.append(args)
        b.wrappedCallRemote = fake
        
        m = getattr(b, meth)
        m(*args)
        expected = tuple([meth] + list(args))
        self.assertEqual(called, [expected])


    def test_build(self):
        self.tr('build', 'something')    


    def test_addBuilder(self):
        self.tr('addBuilder', 'something')


    def test_remBuilder(self):
        self.tr('remBuilder', 'something')
    
    
    def test_remObserver(self):
        self.tr('remObserver', 'something')


    def test_addObserver(self):
        self.tr('addObserver', 'something')
    
    
    def test_noteReceived(self):
        self.tr('noteReceived', 'something')
    
    
    def test_eq(self):
        """
        If my original is equal, I am equal
        """
        a = RemoteHub('foo')
        b = RemoteHub('foo')
        self.assertEqual(a, b, "They should be equal because they wrap the "
                         "same original")
    
    
    def test_disconnectMe(self):
        """
        Disconnect this remoteHub from his hub by removing builders
        and observers.
        """
        a = RemoteHub('foo')
        a.hub = Hub()
        
        calledO = []
        a.hub.remObserver = calledO.append
        
        calledB = []
        a.hub.remBuilder = calledB.append
        
        a.disconnectMe()
        
        self.assertEqual(calledO, [a],
            "Should call remObserver")
        self.assertEqual(calledB, [a],
            "Should call remBuilder")


    def test_wrappedCallRemote(self):
        """
        If command succeed, nothing happens
        """
        f = FakeReference()
        a = RemoteHub(f)
        d = a.wrappedCallRemote('foo')
        self.assertTrue(isinstance(d, defer.Deferred))
        f.result.callback(None)
        return d
    
    
    def catchAsyncError(self, exception):
        """
        I test that if callRemote returns an asynchronous exception
        """
        ref = FakeReference()
        hub = RemoteHub(ref)
        
        # fake out disconnectMe
        hub.disconnectMe_called = []
        def disconnectMe():
            hub.disconnectMe_called.append(True)
        hub.disconnectMe = disconnectMe

        d = hub.wrappedCallRemote('foo')
        self.assertTrue(isinstance(d, defer.Deferred))
        
        # make sure no error is returned
        def eb(r):
            self.fail("Should trap the error: %s" % r)
        d.addErrback(eb)
        
        # cause error
        ref.result.errback(exception)
        
        self.assertEqual(hub.disconnectMe_called, [True],
            "disconnectMe should be called")
        return d


    def test_wrappedCallRemote_DeadReferenceError(self):
        """
        If a DeadReferenceError is raised, call disconnectMe
        """
        return self.catchAsyncError(pb.DeadReferenceError())


    def test_wrappedCallRemote_PBConnectionLost(self):
        """
        If the connection is lost, call disconnectMe
        """
        return self.catchAsyncError(pb.PBConnectionLost())


    def test_wrappedCallRemote_syncConnLost(self):
        """
        If the connection is lost and the error is raised synchronously by
        callRemote, call disconnectMe
        """
        ref = FakeReference()
        hub = RemoteHub(ref)
        
        # fake out disconnectMe
        hub.disconnectMe_called = []
        def disconnectMe():
            hub.disconnectMe_called.append(True)
        hub.disconnectMe = disconnectMe
        
        # fake the error
        def bad(*args):
            raise pb.PBConnectionLost('oh no')
        ref.callRemote = bad
        
        hub.wrappedCallRemote('foo')
        self.assertEqual(hub.disconnectMe_called, [True])



class HubShellTest(TestCase):
    """
    I test the shell aspects of the Hub
    """
    
    def test_startShell(self):
        """
        
        """
