from twisted.internet import defer, utils
from twisted.python.filepath import FilePath


class FileNotFoundError(Exception): pass



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

    
    def run(self, version):
        """
        Start this Build (whatever that means) with the given version
        """
        raise NotImplementedError("You must override this method")



class FileBuild(Build):
    """
    I wrap an executable file for building.
    """
    
    def __init__(self, path):
        Build.__init__(self)
        if isinstance(path, FilePath):
            self.path = path
        else:
            self.path = FilePath(path)
    
    
    def run(self, version):
        """
        Run the file.
        """
        if not self.path.exists():
            raise FileNotFoundError('File not found')
        d = utils.getProcessValue(self.path.path, args=(version,))
        d.addCallback(self.finish)

        

