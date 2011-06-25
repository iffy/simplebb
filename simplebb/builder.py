import datetime

from zope.interface import implements
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder, IEmitter
from simplebb.build import FileBuild
from simplebb.report import Emitter
from simplebb.util import generateId



class Builder:
    """
    I am an abstract Builder that can't actually build anything.
    
    I set my uid on initialization.  My name can be chosen.
    """
    
    implements(IBuilder)
    
    uid = None
    
    name = 'Builder'
    
    def __init__(self):
        self.uid = '%s-%s' % (self.__class__.__name__, generateId())
        self._pastRequestIds = set([])


    def build(self, request):
        """
        Initial set up of a request.
        """
        if 'uid' not in request:
            request['uid'] = '%s-%s' % ('req', generateId())
        if 'time' not in request:
            request['time'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %f%Z')
        
        if request['uid'] not in self._pastRequestIds:
            self._pastRequestIds.add(request['uid'])
            self._build(request)
        
        return request
    
    
    def _build(self, request):
        """
        Actually do the build
        """



class FileBuilder(Builder, Emitter):
    """
    I create and run FileBuilds found from my root directory.
    """
    
    implements(IBuilder)
    
    path = None

    
    def __init__(self, path=None):
        Emitter.__init__(self)
        Builder.__init__(self)
        
        if isinstance(path, FilePath):
            self.path = path
        elif path is not None:
            self.path = FilePath(path)


    def _build(self, request):
        """
        Find the build in the file system and start it.
        """
        project = request['project']
        test_path = request['test_path']
        version = request['version']
        
        builds = self.findBuilds(project, test_path)
        for build in builds:
            build.version = version
            build.req_uid = request['uid']
            build.run()
            
            self.emit(build.makeNote('start'))
            
            def emitDone(build, self):
                self.emit(build.makeNote('done'))
            
            build.done.addCallback(emitDone, self)
        

    def _findHeads(self, project, test_path=None):
        """
        Find the directory roots for a given project and test_path
        """
        project_fp = self.path.child(project)
        if project_fp.exists():
            if test_path:
                for child in project_fp.globChildren(test_path):
                    yield child
            else:
                yield project_fp
    
    
    def _getChildFiles(self, root):
        """
        Given the root file/directory, return all the file descendents
        """
        if root.isdir():
            for child in root.walk():
                if child.isfile():
                    yield child
        else:
            yield root

    
    def findBuilds(self, project, test_path=None):
        """
        Return a list of FileBuilds that match the given criteria
        """
        project_root = list(self._findHeads(project))
        if not project_root:
            return
        project_prefix = len(project_root[0].path) + 1
        
        heads = self._findHeads(project, test_path)
        for head in heads:
            for child in self._getChildFiles(head):
                # find test_path
                b = FileBuild(child)
                b.project = project
                b.test_path = child.path[project_prefix:]
                b.builder = self
                yield b











