from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder, IEmitter
from simplebb.builder import Builder, FileBuilder
from simplebb.build import FileBuild, Build



class BuilderTest(TestCase):
    
    
    def test_IBuilder(self):
        verifyClass(IBuilder, Builder)
        verifyObject(IBuilder, Builder())
    
    
    def test_uid(self):
        b = Builder()
        self.assertNotEqual(b.uid, None)
        self.assertTrue(b.uid.startswith('Builder-'), b.uid)
    
    
    def test_build_basic(self):
        """
        Should accept the basic requirements.
        """
        r = {
            'project': 'foo',
            'version': 'bar',
        }
        b = Builder()
        ret = b.build(r)
        self.assertEqual(ret, r, "Should return the filled-out build request")
    
    
    def test_build_uid(self):
        """
        Should populate uid if it's not there.
        """
        b = Builder()
        r = dict(project='foo', version='bar')
        
        b.build(r)
        self.assertNotEqual(r['uid'], None)
        
        uid = r['uid']
        
        b.build(r)
        self.assertEqual(r['uid'], uid, "Should not overwrite the uid")
    
    
    def test_build_start(self):
        """
        Should populate start time if it's not there
        """
        b = Builder()
        r = dict(project='foo', version='bar')
        
        b.build(r)
        self.assertNotEqual(r['time'], None)
        
        t = r['time']
        
        import time
        time.sleep(0.01)
        
        b.build(r)
        self.assertEqual(r['time'], t, "Should not overwrite the time")
    
    
    def test_build_build(self):
        """
        Build should pass the build on to _build
        """
        b = Builder()
        
        called = []
        b._build = called.append
        
        r = dict(project='foo', version='bar')
        
        b.build(r)
        self.assertEqual(called, [r])
    
    
    def test__build(self):
        """
        Should be overwritten
        """
        b = Builder()
        self.assertEqual(None, b._build({}))
    
    
    def test_build_alreadyRequested(self):
        """
        Requests for builds will only be passed to _build once
        per uid
        """
        b = Builder()
        
        called = []
        b._build = called.append
        
        r = dict(project='foo', version='bar', uid='something')
        
        b.build(r)
        self.assertEqual(called, [r])
        
        b.build(r)
        self.assertEqual(called, [r],
            "Should not have sent to _build this time")
           




class FileBuilderTest(TestCase):
    
    
    def test_IBuilder(self):
        verifyClass(IBuilder, FileBuilder)
        verifyObject(IBuilder, FileBuilder())
    
    
    def test_IEmitter(self):
        verifyClass(IEmitter, FileBuilder)
        verifyObject(IEmitter, FileBuilder())
    
    
    def test_subclass(self):
        """
        Should inherit from Builder
        """
        self.assertTrue(issubclass(FileBuilder, Builder))


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


    def test__build(self):
        """
        _build should
            - get the results of findBuilds,
            - set the version attribute of each Build,
            - call run() on each Build,
            - pass each Build.toDict through emit
            - wait on the Build's completion to send the finished build.toDict
              through emit.
        """
        b = FileBuilder('foo')
        
        r = [Build()]
        
        # fake out Build.run()
        run_called = []
        def fakerun():
            run_called.append(True)
        r[0].run = fakerun
        
        # fake out findBuilds()
        b.findBuilds = lambda *ign: r
        
        # fake out emit()
        emit_called = []
        b.emit = emit_called.append
        
        
        b._build(dict(version='version', project='foo', test_path='bar'))
        
        
        # version should be set on the Build
        self.assertEqual(r[0].version, 'version',
            "Should have set the version on the Build")
        
        self.assertEqual(run_called, [True],
            "Build.run() should have been called")
        
        self.assertEqual(emit_called, [r[0].toDict()],
            "Builder.emit() should have been called")
        
        # reset the fake
        emit_called.pop()
        
        # finish the build manually.
        r[0].done.callback(r[0])
        
        self.assertEqual(emit_called, [r[0].toDict()],
            "When the build finishes, Builder.emit should be called")



