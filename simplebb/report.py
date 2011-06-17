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
        Register this observer to receive buildReceived notifications.
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    
    def remObserver(self, observer):
        """
        Unregister an observer from receiving buildReceived notifications.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    
    def emit(self, buildDict):
        """
        Emit to all my observer's buildReceived method the given buildDict
        """
        # don't allow repeats
        h = hashlib.sha256(unicode(buildDict)).hexdigest()
        if h in self._handled:
            return
        self._handled.append(h)
        
        for o in self._observers:
            o.buildReceived(buildDict)


