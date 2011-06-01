from twisted.spread import pb
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




