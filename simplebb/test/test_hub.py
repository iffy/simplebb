from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.hub import Hub



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


    def test_requestBuild(self):
        """
        Should pass it along to all registered builders.
        """
        class FakeBuilder:
            def requestBuild(self, *args, **kw):
                self.called = args, kw
        
        b = FakeBuilder()
        h = Hub()
        h.addBuilder(b)
        h.requestBuild('version', 'project', 'test_path')
        self.assertEqual(b.called[0], ('version', 'project'))
        self.assertEqual(b.called[1]['test_path'], 'test_path')


