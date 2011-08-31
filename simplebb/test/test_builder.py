from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyClass, verifyObject
from twisted.python.filepath import FilePath

from simplebb.interface import IBuilder, IPublisher
from simplebb.builder import FileBuilder
from simplebb.note import BuildRequest, Note

import json


class FileBuilderTest(TestCase):
    
    
    timeout = 1

    
    def test_IBuilder(self):
        verifyClass(IBuilder, FileBuilder)
        verifyObject(IBuilder, FileBuilder())


    def test_IPublisher(self):
        verifyClass(IPublisher, FileBuilder)
        verifyObject(IPublisher, FileBuilder())
    

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


    def test_findScript(self):
        """
        Should return the file named by findScript
        """
        f = FilePath('bar')
        b = FileBuilder(f)
        r = b.findScript('foobar')
        self.assertEqual(r, FilePath('bar').child('foobar'))


    def test_build(self):
        """
        Should execute the script returned by findScript with the version
        passed in as an arg.
        """
        script = FilePath(self.mktemp())
        script.setContent('#!/bin/bash\necho "version:$1"\nexit 24')
        
        b = FileBuilder()
        b.name = 'bob'
        
        called = []
        def findScript(project):
            called.append(project)
            return script
        b.findScript = findScript
        
        pubbed = []
        b.publish = pubbed.append
        
        build_req = BuildRequest('project', 'version')
        d = b.build(build_req)
        
        
        self.assertEqual(called, ['project'])
        
        def check(result):
            self.assertEqual(result, 24)
            
            # should publish the start and stop
            self.assertEqual(len(pubbed), 2)
            n = pubbed[0]
            self.assertTrue(isinstance(n, Note))
            self.assertEqual(n.builder, 'bob')
            self.assertEqual(n.project, 'project')
            self.assertEqual(n.version, 'version')
            self.assertEqual(n.build_uid, build_req.uid)
            self.assertEqual(n.body, json.dumps({'event': 'start'}))
            
            n = pubbed[1]
            self.assertTrue(isinstance(n, Note))
            self.assertEqual(n.builder, 'bob')
            self.assertEqual(n.project, 'project')
            self.assertEqual(n.version, 'version')
            self.assertEqual(n.build_uid, build_req.uid)
            self.assertEqual(n.body, json.dumps({'event': 'end', 'status': 24}))
        
        return d.addCallback(check)


    def test_subscribe(self):
        """
        Should store the function in _subscribed
        """
        b = FileBuilder()
        called = []
        b.subscribe(called.append)
        b.publish('something')
        self.assertEqual(called, ['something'])


    def test_unsubscribe(self):
        """
        Should stop messages
        """
        b = FileBuilder()
        called = []
        b.unsubscribe(called.append)
        
        b.subscribe(called.append)
        b.unsubscribe(called.append)
        b.publish('something')
        self.assertEqual(called, [])


    def test_build_noScript(self):
        """
        If there's no script, don't do anything
        """
        b = FileBuilder()
        b.findScript = lambda x:None
        return b.build(BuildRequest('foo', 'bar'))


