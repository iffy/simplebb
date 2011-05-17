from twisted.trial.unittest import TestCase
from twisted.protocols.basic import LineReceiver


from simplebb.shell import ShellProtocol



class ShellProtocolTest(TestCase):
    
    
    def setUp(self):
        self.s = ShellProtocol()
    
    
    def test_lineReceiver(self):
        """
        Should be a LineReceiver
        """
        self.assertTrue(issubclass(ShellProtocol, LineReceiver))
    
    
    def t(self, i, expected_output):
        s = ShellProtocol()
        r = s.parseCmd(i)
        self.assertEqual(r, expected_output, "From parseCmd(%r)" % i)

    
    def test_parse_normal(self):
        self.t('something cool', ['something', 'cool'])


    def test_parse_strip(self):
        self.t(' something cool ', ['something', 'cool'])
    
    
    def test_parse_singlequote(self):
        self.t("hello 'some one'", ['hello', 'some one'])
    
    
    def test_parse_doublequote(self):
        self.t('foo "bar baz " hey', ['foo', 'bar baz ', 'hey'])
    
    
    def test_cmd_build(self):
        """
        build just passes on through
        """
        called = []
        
        class FakeBrain:
        
            def buildProject(self, project, version, test=None):
                called.append((project, version, test))
                
        class FakeFactory: pass


        factory = FakeFactory()
        factory.brain = FakeBrain()
        
        s = ShellProtocol()
        s.factory = factory
        
        s.cmd_build('foo', 'bar')
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], ('foo', 'bar', None))
        
        called.pop()
        s.cmd_build('foo', 'bar', 'test1')
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], ('foo', 'bar', 'test1'))
    
    
    def test_getCommands(self):
        """
        Should return a dictionary where the key is the command name
        and the value is the function called to run the command.
        """
        s = ShellProtocol()
        def f():
            pass
        s.cmd_something = f
        c = s.getCommands()
        self.assertEqual(c['something'], f)
    
    
    def test_getCommands_cache(self):
        """
        getCommands should cache the results
        """
        s = ShellProtocol()
        c = s.getCommands()
        def f():
            pass
        s.cmd_something = f
        c2 = s.getCommands()
        self.assertEqual(c, c2)
    
    
    def test_runCmd(self):
        """
        runCmd should find the command from arg[0] and run it with args[1:]*
        """
        s = ShellProtocol()
        
        called = []
        def fake(*args):
            called.append(args)
            return 'hey'
        
        s.cmd_foo = fake
        
        r = s.runCmd(*['foo', 'arg1', 'arg2', 'arg3'])
        self.assertEqual(r, 'hey')
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], ('arg1', 'arg2', 'arg3'))
    
    
    def test_runCmd_noCmd(self):
        """
        if there's no such command, tell the person so
        """
        s = ShellProtocol()
        called = []
        s.sendLine = called.append
        
        r = s.runCmd(*['foo', 'bar'])
        self.assertEqual(r, False)
        self.assertEqual(len(called), 1)
        self.assertTrue('foo' in called[0])
    
    
    def test_runCmd_badArgs(self):
        """
        If the user supplies bad arguments
        """
        s = ShellProtocol()
        called = []
        s.sendLine = called.append
        
        def fake(arg1, arg2):
            pass
        
        s.cmd_foo = fake
        
        r = s.runCmd(*['foo', 'arg1'])
        self.assertEqual(r, False)
        self.assertEqual(len(called), 1)
    
    
    def test_runCmd_error(self):
        """
        If there's any other kind of error
        """
        s = ShellProtocol()
        called = []
        s.sendLine = called.append
        
        def fake(arg1):
            raise Exception('foo')
        s.cmd_foo = fake
        
        r = s.runCmd(*['foo', 'arg1'])
        self.assertEqual(r, False)
        self.assertEqual(len(called), 1)














