from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject

from twisted.internet.endpoints import clientFromString
from twisted.internet import reactor
from twisted.spread import pb

from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.hub import Hub
from simplebb.builder import Builder



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
    
    
    def test_buildReceived(self):
        """
        Should just call emit
        """
        h = Hub()
        called = []
        h.emit = called.append
        h.buildReceived('something')
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


    def test_removeBuilder(self):
        """
        Should remove from the _builders list
        """
        h = Hub()
        o = object()
        h._builders = [o]
        h.removeBuilder(o)
        self.assertEqual(h._builders, [])
        h.removeBuilder(o)
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
    
    
    def test_getServerFactory(self):
        """
        Should return an instance of pb.PBServerFactory with self passed in.
        """
        h = Hub()
        f = h.getServerFactory()
        self.assertTrue(isinstance(f, pb.PBServerFactory))
        self.assertEqual(f.root, h)
    
    
    def test_startServer(self):
        """
        Should call twisted.internet.endpoints.serverFromString and hook that
        up to getServerFactory
        """
        h = Hub()
        h.remote_echo = lambda x: x
        h.startServer('tcp:10999')
        
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
        d = h.startServer('tcp:10999')
        d.addCallback(lambda x: h.startServer('tcp:10888'))
        
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
        You can connect to other servers
        """
        sh = Hub()
        ch = Hub()
        called = []
        ch.gotRemoteRoot = called.append
        
        sh.startServer('tcp:10999')
        
        d = ch.connect('tcp:host=127.0.0.1:port=10999')
        d.addCallback(lambda x: self.assertEqual(len(called), 1,
            "Should have called .gotRemoteRoot"))
        d.addCallback(lambda x: ch.disconnect('tcp:host=127.0.0.1:port=10999'))
        d.addCallback(lambda x: sh.stopServer('tcp:10999'))
        return d
        
        
        






