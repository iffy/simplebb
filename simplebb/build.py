from twisted.internet import defer, utils
from twisted.python.filepath import FilePath
from zope.interface import Interface, implements


from simplebb.interface import IBuild
from simplebb.util import generateId



FILE_NOT_FOUND = 404
MISSING_VERSION = 400



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
        self.uid = generateId()
    
    
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
    
    
    def toDict(self):
        """
        Return a dictionary representation of this Build
        """
        return dict(
            uid=self.uid,
            status=self.status,
            project=self.project,
            version=self.version,
            test_path=self.test_path,
            runtime=self.runtime)



class FileBuild(Build):
    """
    I am a build of a single file.
    """
    
    def __init__(self, path):
        Build.__init__(self)
        if isinstance(path, FilePath):
            self._filepath = path
        else:
            self._filepath = FilePath(path)

    
    def run(self):
        """
        Executes _filepath and eventually calls _finish.
        """
        if not self.version:
            return self._finish(MISSING_VERSION)
        if not self._filepath.exists():
            return self._finish(FILE_NOT_FOUND)
        d = utils.getProcessValue(self._filepath.path, args=(self.version,))
        d.addCallback(self._finish)


