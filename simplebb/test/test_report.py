from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from simplebb.interface import IEmitter
from simplebb.report import Emitter



class EmitterTest(TestCase):


    def test_IEmitter(self):
        verifyClass(IEmitter, Emitter)
        verifyObject(IEmitter, Emitter())


    def test_addObserver(self):
        """
        You should be able to add Observers.
        """
        e = Emitter()
        o = object()
        e.addObserver(o)
        self.assertTrue(o in e._observers)
        
        e.addObserver(o)
        self.assertEqual(e._observers.count(o), 1,
            "Observers should not be added multiple times")
    
    
    def test_removeObservers(self):
        """
        You should be able to remove observers.
        """
        e = Emitter()
        o = object()
        e.addObserver(o)
        
        e.removeObserver(o)
        self.assertFalse(o in e._observers)
        
        e.removeObserver(o)
        self.assertFalse(o in e._observers)
    
    
    def test_emit(self):
        """
        Should call each observers buildReceived method.
        """        
        class FakeObserver:
            def buildReceived(self, buildDict):
                self.build = buildDict
        
        e = Emitter()
        
        observers = [FakeObserver(), FakeObserver()]
        for o in observers:
            e.addObserver(o)
        
        
        e.emit('something')
        self.assertEqual([x.build for x in observers], ['something', 'something'])

