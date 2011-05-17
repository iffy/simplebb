from twisted.internet import defer, utils
from twisted.python.filepath import FilePath
from zope.interface import Interface, implements


class FileNotFoundError(Exception): pass



class IBuilder(Interface):
    """
    Things that implement me allow you to build projects.
    """
    
    def buildProject(project, version, test=None):
        """
        Starts a project building.
        """
    
    
    def notifyBuilt(func):
        """
        Register a function to be called whenever a project is finished building.
        """



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

        

class ProjectRepo:
    """
    I wrap the directory where project build steps are stored.  You can ask me to build projects.
    """
    
    implements(IBuilder)
    
    def __init__(self, path=None):
        if isinstance(path, FilePath) or path is None:
            self.path = path
        else:
            self.path = FilePath(path)
        self._notifyBuiltFuncs = []
    
    
    def getBuilds(self, project, test=None):
        """
        Return a generator of a list of FileBuilds that should be built.
        
        project     string name of project that corresponds to file/dir in self.path
        
        test        optional test file name if the inside the project dir
        """
        project_path = self.path.child(project)
        if project_path.isfile():
            # file
            if test is None:
                yield FileBuild(project_path)
        else:
            # directory
            glob_pattern = test or '*'
            for child in project_path.globChildren(glob_pattern):
                yield FileBuild(child)
    
    
    def runBuilds(self, builds, version):
        """
        Run the given builds for the given version
        """
        ret = []
        for build in builds:
            build.run(version)
            ret.append(build.done)
        return ret
    
    
    def buildProject(self, project, version, test=None):
        """
        Builds a project of a given version.
        
        Returns a list of Deferreds that will fire with Build objects on completion
        of the tests.
        """
        builds = self.getBuilds(project, test)
        self.runBuilds(builds, version)
    
    
    def notifyBuilt(self, func):
        """
        Register a function to be called whenever a build finishes
        """
        self._notifyBuiltFuncs.append(func)






