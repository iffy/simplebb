from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder
from simplebb.builder import FileSystemBuilder



class FileSystemBuilderTest(TestCase):
    
    
    def test_IBuilder(self):
        verifyClass(IBuilder, FileSystemBuilder)
    
    
    def test_init(self):
        """
        Should have a base path.
        """
        f = FileSystemBuilder()
        self.assertEqual(f.path, None)


    def test_init_str(self):
        """
        Initializing with a string signifies a path
        """
        f = FileSystemBuilder('foo')
        self.assertEqual(f.path, FilePath('foo'))
    
    
    def test_init_FilePath(self):
        """
        Init with a FilePath is passed straight through
        """
        f = FilePath('bar')
        b = FileSystemBuilder(f)
        self.assertEqual(b.path, f)


    def test_findBuilds_singleFile(self):
        """
        if a project is a single file, return a Build for that project.
        """
        f = FilePath(self.mktemp())
        b = FileSystemBuilder(f)
        

    def test_requestBuild(self):
        """
        requesting a build
        """