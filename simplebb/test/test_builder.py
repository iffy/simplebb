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

    
    
class findBuildsTest(TestCase):

    
    def setUp(self):
        f = FilePath(self.mktemp())
        
        foo = f.child('foo')
        test1 = foo.child('test1')
        test2 = foo.child('test2')
        bar = foo.child('bar')
        test3 = bar.child('test3')
        
        bar.makedirs()
        
        test1.setContent('test1')
        test2.setContent('test2')
        test3.setContent('test3')
        
        self.b = FileSystemBuilder(f)


    def test_singleFile(self):
        """
        if a project is a single file, return a Build for that project.
        """
        f = FilePath(self.mktemp())
        f.makedirs()
        b = FileSystemBuilder(f)
        
        # no file
        r = b.findBuilds('foo')
        self.assertEqual(list(r), [])
        
        # file
        f.child('foo').setContent('something')
        r = list(b.findBuilds('foo'))
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].project, 'foo')
        self.assertEqual(r[0].builder, b)
        self.assertEqual(r[0].test_path, None)
    
        # test_path given, more specific than foo
        r = list(b.findBuilds('foo', 'something'))
        self.assertEqual(len(r), 0)


    def test_noTestPath(self):
        """
        If no testpath supplied, return everything under the path
        """
        r = list(self.b.findBuilds('foo'))
        self.assertEqual(len(r), 3)
        self.assertEqual(set([x.project for x in r]), set(['foo']))
        self.assertEqual(set([x.test_path for x in r]), set(['test1', 'test2', 'bar/test3']))












