import random
import hashlib
import time
import datetime

from zope.interface import implements
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder, IEmitter
from simplebb.build import FileBuild
from simplebb.report import Emitter



_idcount = 0

def generateId():
    """
    Returns a uniqueish id.
    """
    global _idcount
    _idcount += 1
    random_part = hashlib.sha1(str(random.getrandbits(256))).hexdigest()
    time_part = datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    num_part = str(_idcount)
    return '%s.%s.%s' % (num_part, time_part, random_part)



class FileBuilder(Emitter):
    """
    I create and run FileBuilds found from my root directory.
    """
    
    implements(IBuilder)
    
    name = None
    
    uid = None
    
    path = None

    
    def __init__(self, path=None):
        Emitter.__init__(self)
        
        if isinstance(path, FilePath):
            self.path = path
        elif path is not None:
            self.path = FilePath(path)


    def requestBuild(self, version, project, test_path=None, reqid=None):
        """
        Find the build in the file system and start it.
        """
        builds = self.findBuilds(project, test_path)
        for build in builds:
            build.version = version
            build.run()
            
            self.emit(build.toDict())
            
            def emitDone(build, self):
                self.emit(build.toDict())
            
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











