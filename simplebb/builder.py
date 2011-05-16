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

        

class ProjectRepo:
    """
    I wrap the directory where project build steps are stored.
    """
    
    def __init__(self, path=None):
        if isinstance(path, FilePath) or path is None:
            self.path = path
        else:
            self.path = FilePath(path)
    
    
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
        for build in builds:
            self.monitorBuild(build)
            build.run(version)
    
    
    def monitorBuild(self, build):
        """
        Monitor a build for completion
        """
        def eb(r):
            return r.value
        build.done.addErrback(eb)
        build.done.addCallback(self.buildDone)






