from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder
from simplebb.builder import FileBuilder
from simplebb.build import FileBuild



class FileBuilderTest(TestCase):
    
    
    def test_IBuilder(self):
        verifyClass(IBuilder, FileBuilder)
    
    
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


    def test_findHeads_project(self):
        """
        Find heads with only a project given should find a single FilePath
        if it exists
        """
        root = FilePath(self.mktemp())
        root.makedirs()
        b = FileBuilder(root)
        
        # dne
        r = list(b._findHeads('foo'))
        self.assertEqual(r, [], "Should not find paths that don't exist")
        
        # exists
        root.child('foo').setContent('gobbledegook')
        r = list(b._findHeads('foo'))
        self.assertEqual(r, [root.child('foo')])
    
    
    def test_findHeads_testPath(self):
        """
        Find heads should find all the heads that match the given testPath
        """
        root = FilePath(self.mktemp())
        
        foo = root.child('foo')
        foo.makedirs()
        test1 = foo.child('test1')
        test2 = foo.child('test2')
        bar = foo.child('bar')
        baz = bar.child('baz')
        
        test1.setContent('test1')
        test2.setContent('test2')
        bar.makedirs()
        baz.setContent('baz')
        
        b = FileBuilder(root)
        
        r = list(b._findHeads('foo', '*'))
        self.assertEqual(len(r), 3, "Should find all the heads with *")
        self.assertEqual(set(r), set([test1, test2, bar]))
        
        r = list(b._findHeads('foo', 'test*'))
        self.assertEqual(len(r), 2)
        self.assertEqual(set(r), set([test1, test2]))
        
        # subdirectory
        r = list(b._findHeads('foo', 'bar/baz'))
        self.assertEqual(r, [baz])


    def test_getChildFiles_file(self):
        """
        Given a file, return the file
        """
        root = FilePath(self.mktemp())
        root.setContent('something')
        b = FileBuilder()
        r = list(b._getChildFiles(root))
        self.assertEqual(r, [root])


    def test_getChildFiles_dir(self):
        """
        Given a directory, return all children files.
        """
        root = FilePath(self.mktemp())
        dir1 = root.child('dir1')
        dir2 = dir1.child('dir2')
        dir2.makedirs()
        
        f1 = root.child('f1')
        f2 = dir1.child('f2')
        f3 = dir2.child('f3')
        
        f1.setContent('foo')
        f2.setContent('foo')
        f3.setContent('foo')
        
        b = FileBuilder()
        
        r = b._getChildFiles(root)
        self.assertEqual(set(r), set([f1, f2, f3]),
            "Should find all files that are descendants")
        
        r = b._getChildFiles(dir1)
        self.assertEqual(set(r), set([f2, f3]))


    def test_findBuilds(self):
        """
        It should call a few functions, passing their results around,
        ending up with FileBuild instances with the correct properties set.
        """
        root = FilePath(self.mktemp())
        project = root.child('project')
        project.makedirs()
        
        foo = project.child('foo')
        bar = project.child('bar')
        foo.setContent('foo')
        bar.setContent('bar')
        
        b = FileBuilder(root)
        
        class Spy:
            
            def __init__(self, func):
                self.func = func
                self.called = []
            
            def __call__(self, *args):
                self.called.append(args)
                return self.func(*args)


        b._findHeads = Spy(b._findHeads)
        b._getChildFiles = Spy(b._getChildFiles)
        
        r = list(b.findBuilds('project', '*'))
        
        self.assertTrue(b._findHeads.called)
        self.assertTrue(('project', '*') in b._findHeads.called)
        
        self.assertEqual(len(b._getChildFiles.called), 2)
        
        self.assertTrue(isinstance(r[0], FileBuild))
        self.assertEqual(r[0].project, 'project')
        self.assertEqual(r[0].test_path, 'foo')
        self.assertEqual(r[0].builder, b)
        self.assertEqual(r[0]._filepath, foo)
        
        self.assertTrue(isinstance(r[1], FileBuild))
        self.assertEqual(r[1].project, 'project')
        self.assertEqual(r[1].test_path, 'bar')
        self.assertEqual(r[1].builder, b)
        self.assertEqual(r[1]._filepath, bar)
        
        self.assertEqual(len(r), 2)




