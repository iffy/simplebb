from zope.interface import implements


from simplebb.interface import IBuilder, IEmitter, IObserver, IBuilderHub
from simplebb.report import Emitter
from simplebb.builder import generateId



class Hub(Emitter):
    """
    I am a build server instance's central hub.
    """
    
    uid = None
    
    implements(IBuilder, IEmitter, IObserver, IBuilderHub)


    def __init__(self):
        Emitter.__init__(self)
        self._builders = []

    
    def buildReceived(self, buildDict):
        """
        Just emit it to my reporters.
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
    
    
    def requestBuild(self, version, project, test_path=None, reqid=None):
        """
        Pass along any new build request to my builders.
        """
        if reqid is None:
            reqid = self.uid + '.' + generateId()
        for builder in self._builders:
            builder.requestBuild(version, project, test_path=test_path, reqid=reqid)




