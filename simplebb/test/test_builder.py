from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder
from simplebb.builder import FileBuilder, ReportableMixin
from simplebb.build import FileBuild, Build


class ReportableMixinTest(TestCase):
    
    
    def test_addReporter(self):
        """
        Reporters can be added.
        """
        b = ReportableMixin()
        self.assertEqual(b._reporters, [])
        o = object()
        b.addReporter(o)
        self.assertEqual(b._reporters, [o])

        b.addReporter(o)
        self.assertEqual(b._reporters, [o],
            "Reports should only be added once")
    
    
    def test_removeReporter(self):
        """
        Reports can be removed.
        """
        b = ReportableMixin()
        o = object()
        b._reporters = [o]
        b.removeReporter(o)
        self.assertEqual(b._reporters, [])
        
        b.removeReporter(o)
        self.assertEqual(b._reporters, [])
    
    
    def test_report(self):
        """
        Reporters are called with .report()
        """
        b = ReportableMixin()
        c1 = []
        c2 = []
        b.addReporter(c1.append)
        b.addReporter(c2.append)
        
        b.report('something')
        self.assertEqual(c1, ['something'])
        self.assertEqual(c2, ['something'])



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
        # project/
        project = root.child('project')
        project.makedirs()
        
        # project/foo
        foo = project.child('foo')
        # project/bar
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
        
        expected = set([
            ('project', 'foo', b, foo),
            ('project', 'bar', b, bar),
        ])
        
        actual = [(x.project, x.test_path, x.builder, x._filepath) for x in r]
        
        self.assertEqual(expected, set(actual))        
        self.assertEqual(len(r), 2)


    def test_requestBuild(self):
        """
        requestBuild should pass the results of findBuilds through
        report()
        """
        b = FileBuilder('foo')
        
        # fake out some stuff
        r = [Build()]
        
        run_called = []
        def fakerun():
            run_called.append(True)
        r[0].run = fakerun
        
        b.findBuilds = lambda *ign: r
        
        report_called = []
        b.report = report_called.append
        
        b.requestBuild('version', 'foo', 'bar')
        
        # version should be set on the Build
        self.assertEqual(r[0].version, 'version')
        
        self.assertEqual(run_called, [True],
            "Build.run should have been called")
        
        self.assertEqual(report_called, [r[0]],
            "Build.report should have been called")
        
        r[0].done.callback(r[0])
        
        self.assertEqual(report_called, [r[0], r[0]],
            "When the build finishes, report should be called")
        


