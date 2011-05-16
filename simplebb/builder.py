from twisted.internet import defer
from twisted.python.filepath import FilePath



class Build:
    """
    I am a build.  I contain the result of the build after my
    done Deferred fires.
    """
    
    status = None
    
    def __init__(self):
        self.done = defer.Deferred()
    
    
    def finish(self, status):
        """
        Mark this build as done with the given integer status
        """
        self.status = status
        if self.status:
            self.done.errback(self)
        else:
            self.done.callback(self)



class FileBuild(Build):
    """
    I wrap an executable file for building.
    """
    
    def __init__(self, path):
        self.path = FilePath(path)

