from twisted.trial.unittest import TestCase
from twisted.python.filepath import FilePath
from twisted.internet import defer
from zope.interface.verify import verifyClass


from simplebb.builder import ProjectRepo, FileBuild, Build, IBuilder
from simplebb.builder import FileNotFoundError



class BuildTest(TestCase):


    timeout = 1
    
    
    def test_doneDeferred(self):
        """
        A Build should have a done Deferred.
        """
        b = Build()
        self.assertTrue(isinstance(b.done, defer.Deferred))
    
    
    def test_status(self):
        b = Build()
        self.assertEqual(b.status, None)
    
    
    def test_getTag(self):
        b = Build()
        self.assertEqual(b.getTag(), dict(project=None, version=None, test=None))
        b.project = 'foo'
        self.assertEqual(b.getTag()['project'], 'foo')
        b.version = 'version'
        self.assertEqual(b.getTag()['version'], 'version')
        b.test = 'some test'
        self.assertEqual(b.getTag()['test'], 'some test')
    
    
    def test_finish_0(self):
        """
        Finishing a build with 0 means the build succeeded.
        """
        b = Build()
        
        def cb_done(res):
            self.assertEqual(res, b)
        b.done.addCallback(cb_done)
        
        b.finish(0)
        self.assertEqual(b.status, 0)
        
        return b.done
    
    
    def test_finish_1(self):
        """
        Finishing a build with non-zero means the build failed.
        """
        b = Build()
        
        def eb_done(res):
            self.assertEqual(res.value, b)
        def cb_done(res):
            self.fail("Should errback, not callback")
        b.done.addCallbacks(cb_done, eb_done)
        
        b.finish(1)
        self.assertEqual(b.status, 1)
        
        return b.done
    
    
    def test_run(self):
        """
        Build.run is meant to be overwritten
        """
        b = Build()

        def cb(res):
            self.assertEqual(res, b)
        
        b.run('version')
        self.assertEqual(b.status, 0)
        self.assertEqual(b.version, 'version')
        return b.done



class FileBuildTest(TestCase):
    
    timeout = 3
    
    
    def test_subClass(self):
        self.assertTrue(issubclass(FileBuild, Build),
            "FileBuild should subclass Build")

    
    def test_initFilename(self):
        """
        Should save the initialized filename as a FilePath
        """
        f = self.mktemp()
        fb = FileBuild(f)
        self.assertEqual(fb.path, FilePath(f))
        self.assertEqual(fb.test, None)
    
    
    def test_initFilePath(self):
        """
        Should save a given FilePath as as the path
        """
        f = FilePath(self.mktemp())
        fb = FileBuild(f)
        self.assertEqual(fb.path, f)

    
    def test_run(self):
        """
        The file should be run with the version as the first arg
        """
        f = FilePath(self.mktemp())
        f.setContent('#!/bin/bash\nexit $1\n')
        f.chmod(0777)
        
        fb = FileBuild(f)
        def cb(res):
            self.assertEqual(res.status, 0)
        fb.done.addCallback(cb)
        
        fb.run('0')
        self.assertEqual(fb.version, '0')
        return fb.done


    def test_run_version(self):
        """
        The version should be passed as the first arg
        """
        f = FilePath(self.mktemp())
        f.setContent('#!/bin/bash\nexit $1\n')
        f.chmod(0777)
        
        fb = FileBuild(f)
        def cb(res):
            self.fail("Should errback, not callback")
        def eb(res):
            self.assertEqual(res.value.status, 1)
        fb.done.addCallbacks(cb, eb)
        
        fb.run('1')
        
        return fb.done


    def test_run_dne(self):
        """
        A file that does not exist can not be run
        """
        f = FilePath(self.mktemp())
        f.makedirs()
        fb = FileBuild(f.child('foo'))
        self.assertRaises(FileNotFoundError, fb.run, 'version')



class ProjectRepoTest(TestCase):

    
    def test_implements(self):
        verifyClass(IBuilder, ProjectRepo)

    
    def test_path(self):
        """
        Can be initialized with a string filename
        """
        f = FilePath(self.mktemp())
        pr = ProjectRepo(f.path)
        self.assertEqual(pr.path, f)
    
    
    def test_path_filepath(self):
        """
        Can be initialized with a FilePath
        """
        f = FilePath(self.mktemp())
        pr = ProjectRepo(f)
        self.assertEqual(pr.path, f)
    
    
    def test_getBuilds_file(self):
        """
        If the object in the directory that corresponds to a requested
        project is a file, return a FileBuild for that file.
        """
        f = FilePath(self.mktemp())
        f.makedirs()
        foo = f.child('foo')
        foo.setContent('something')
        
        pr = ProjectRepo(f)
        r = list(pr.getBuilds('foo'))
        
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].path, foo)
        self.assertEqual(r[0].project, 'foo',
            "ProjectRepo should set the project attr of the Build")
        self.assertEqual(r[0].test, None)
        self.assertEqual(r[0].version, None)
    
    
    def test_getBuilds_file_withTest(self):
        """
        If the object in the directory that corresponds to a requested
        project is a file, and a specific test is also request, return nothing.
        """
        f = FilePath(self.mktemp())
        f.makedirs()
        foo = f.child('foo')
        foo.setContent('something')
        
        pr = ProjectRepo(f)
        r = list(pr.getBuilds('foo', 'test1'))
        
        self.assertEqual(len(r), 0)
    
    
    def test_getBuilds_dir(self):
        """
        If the project has a directory full of tests, return all of them
        """
        root = FilePath(self.mktemp())
        foo = root.child('foo')
        foo.makedirs()
        test1 = foo.child('test1')
        test1.setContent('content of test1')
        test2 = foo.child('test2')
        test2.setContent('content of test2')
                
        pr = ProjectRepo(root)
        r = list(pr.getBuilds('foo'))
        
        self.assertEqual(len(r), 2)
        self.assertEqual(set([x.path for x in r]), set([test1, test2]))
        self.assertEqual(set([x.project for x in r]), set(['foo']))
    
    
    def test_getBuilds_dir_withTest(self):
        """
        If the project has a directory, a single test may be chosen.
        """
        root = FilePath(self.mktemp())
        foo = root.child('foo')
        foo.makedirs()
        test1 = foo.child('test1')
        test1.setContent('content of test1')
        test2 = foo.child('test2')
        test2.setContent('content of test2')
                
        pr = ProjectRepo(root)
        r = list(pr.getBuilds('foo', 'test1'))
        
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].path, test1)
        self.assertEqual(r[0].project, 'foo')
        self.assertEqual(r[0].test, 'test1')


    def test_runBuilds(self):
        """
        should run each of the builds
        """                
        pr = ProjectRepo()
        
        builds = [Build(), Build()]
        ret = pr.runBuilds(builds, 'foo')
        
        self.assertTrue(builds[0].done.called)
        self.assertEqual(builds[0].version, 'foo')
        
        self.assertTrue(builds[1].done.called)
        self.assertEqual(builds[1].version, 'foo')
        
        self.assertEqual(len(ret), 2, "The Build.done Deferreds should have been returned")
        self.assertEqual(set(ret), set([x.done for x in builds]))


    def test_buildProject(self):
        """
        Should call getBuilds and runBuilds.
        """
        pr = ProjectRepo()
        
        called = []
        def getBuilds(project, test=None):
            called.append((project, test))
            return 'get result'
        pr.getBuilds = getBuilds
        
        def runBuilds(builds, version):
            called.append((builds, version))
            return 'run result'
        pr.runBuilds = runBuilds

        pr.buildProject('foo', 'version 1', 'test 1')
        
        self.assertEqual(called[0], ('foo', 'test 1'))
        self.assertEqual(called[1], ('get result', 'version 1'))
    
    
    def test_notifyBuilt(self):
        """
        notifyBuilt should save a function for calling after something is built
        """
        pr = ProjectRepo()
        self.assertEqual(pr._notifyBuiltFuncs, [])
        
        def f(status):
            pass
        pr.notifyBuilt(f)
        self.assertEqual(pr._notifyBuiltFuncs, [f])
        




