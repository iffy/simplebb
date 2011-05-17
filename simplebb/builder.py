from twisted.internet import defer, utils
from twisted.python.filepath import FilePath
from zope.interface import Interface, implements


from simplebb.interface import IBuild



class FileNotFoundError(Exception): pass



class Build:
    """
    I am a build.  I contain the result of the build after my
    done Deferred fires.
    """
    
    implements(IBuild)
    
    uid = None
    status = None
    project = None
    version = None
    test_path = None
    
    builder = None
    
    done = None
    runtime = None
    
    def __init__(self):
        self.done = defer.Deferred()
    
    
    def _finish(self, status):
        """
        Mark this build as done with the given integer status
        """
        self.status = status
        self.done.callback(self)

    
    def run(self):
        """
        Start this Build (whatever that means) with the given version
        """
        self._finish(self.status)




