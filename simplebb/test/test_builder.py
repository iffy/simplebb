from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder
from simplebb.builder import FileBuilder



class FileBuilderTest(TestCase):
    
    
    def test_IBuilder(self):
        verifyClass(IBuilder, FileBuilder)
        verifyObject(IBuilder, FileBuilder())
    

    def test_init(self):
        """
        Should have a base path.
        """
        f = FileBuilder()
        self.assertEqual(f.path, None)


    def test_init_str(self):
        """
        Initializing with a string signifies a path
        """
        f = FileBuilder('foo')
        self.assertEqual(f.path, FilePath('foo'))
    
    
    def test_init_FilePath(self):
        """
        Init with a FilePath is passed straight through
        """
        f = FilePath('bar')
        b = FileBuilder(f)
        self.assertEqual(b.path, f)


    



