from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject


from simplebb.interface import IEmitter, IObserver
from simplebb.report import Emitter, Observer



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
    
    
    def test_remObservers(self):
        """
        You should be able to remove observers.
        """
        e = Emitter()
        o = object()
        e.addObserver(o)
        
        e.remObserver(o)
        self.assertFalse(o in e._observers)
        
        e.remObserver(o)
        self.assertFalse(o in e._observers)
    
    
    def test_emit(self):
        """
        Should call each observers noteReceived method.
        """        
        class FakeObserver:
            def noteReceived(self, note):
                self.note = note
        
        e = Emitter()
        
        observers = [FakeObserver(), FakeObserver()]
        for o in observers:
            e.addObserver(o)
        
        d = {'uid':'something'}
        
        e.emit(d)
        self.assertEqual([x.note for x in observers], [d, d])
    
    
    def test_emit_repeat(self):
        """
        The same message should not be emitted twice
        """
        class FakeObserver:
            def noteReceived(self, note):
                self.note = note
        
        e = Emitter()
        o = FakeObserver()
        e.addObserver(o)
        
        note = dict(uid='1234')
        
        e.emit(note)
        self.assertEqual(o.note, note)
        
        o.note = None
        e.emit(note)
        self.assertEqual(o.note, None,
            "Should not have passed the report on because it was already"
            "received: %r" % note)



class ObserverTest(TestCase):


    def test_IObserver(self):
        verifyClass(IObserver, Observer)
        verifyObject(IObserver, Observer())


    def noteReceived(self):
    

