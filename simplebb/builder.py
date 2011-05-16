from twisted.internet import defer



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



class FileBuild(object):
    """
    I wrap a file for building.
    """
    
    def __init__(self, filename):
        self.filename = filename



class DirectoryBuilder(object):
    """
    I am a Builder that looks for build instructions from the filesystem.
    """
    
    root = None
    