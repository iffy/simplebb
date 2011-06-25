from zope.interface import implements
from simplebb.interface import IEmitter

import hashlib



class Emitter:
    """
    I emit information about builds.
    """
    
    implements(IEmitter)


    def __init__(self):
        self._observers = []
        self._handled = []


    def addObserver(self, observer):
        """
        Register this observer to receive noteReceived notifications.
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    
    def remObserver(self, observer):
        """
        Unregister an observer from receiving noteReceived notifications.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    
    def emit(self, note):
        """
        Emit to all my observer's noteReceived method the given note
        """
        if note['uid'] in self._handled:
            return
        self._handled.append(note['uid'])
        
        for o in self._observers:
            o.noteReceived(note)


