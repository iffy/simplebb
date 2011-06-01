from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject

from twisted.spread import pb

from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.hub import Hub
from simplebb.builder import Builder



class HubTest(TestCase):
    
    
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




