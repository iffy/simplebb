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
        s.showPrompt = lambda: None
        
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
        s.showPrompt = lambda: None
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
        s.showPrompt = lambda: None
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
        s.showPrompt = lambda: None
        called = []
        s.sendLine = called.append
        
        def fake(arg1):
            raise Exception('foo')
        s.cmd_foo = fake
        
        r = s.runCmd(*['foo', 'arg1'])
        self.assertEqual(r, False)
        self.assertEqual(len(called), 1)
    
    
    def test_help(self):
        """
        Help should spit out the first line of all doc strings of all commands
        """
        class Fake:
            def __init__(self, doc):
                self.__doc__ = doc
        s = ShellProtocol()
        
        foo = Fake('''
        this is something here.
        
        and not here
        ''')
        bar = Fake('''
        bar is this guy''')
        
        s.getCommands = lambda: {'foo': foo, 'bar': bar}
        
        called = []
        s.sendLine = called.append
        
        s.cmd_help()
        
        r = '\n'.join(called)
        
        self.assertTrue('this is something here.' in r)
        self.assertTrue('and not here' not in r, 'Only the first line should be included')
        
        self.assertTrue('bar is this guy' in r)
    
    
    def test_help_one(self):
        """
        Help should display help specific to a command.
        """
        s = ShellProtocol()
        called = []
        s.sendLine = called.append
        
        s.cmd_help('help')
        
        r = '\n'.join(called)
        
        self.assertTrue('usage: help [command]' in r)
        self.assertTrue('You can get specific help' in r)
    
    
    def test_help_nocommand(self):
        """
        Help should tell them if the command doesn't exist
        """
        s = ShellProtocol()
        called = []
        s.sendLine = called.append
        
        s.cmd_help('foobar')
        
        self.assertTrue('foobar' in called[0])
    
    
    def test_lineReceived(self):
        """
        lineReceived should parse the args and call runCmd
        """
        s = ShellProtocol()
        called = []
        def parseCmd(s):
            called.append(('parse', s))
            return ['parsed', 'arg']
        def runCmd(cmd, *args):
            called.append(('run', cmd, args))
        
        s.parseCmd = parseCmd
        s.runCmd = runCmd
        
        s.lineReceived('how are you')
        
        self.assertEqual(len(called), 2)
        self.assertEqual(called[0], ('parse', 'how are you'))
        self.assertEqual(called[1], ('run', 'parsed', ('arg',)))
    
    
    def test_cmd_quit(self):
        """
        Should be able to quit
        """
        called = []
        
        class FakeTransport:
            def loseConnection(self):
                called.append(True)
        
        s = ShellProtocol()
        s.transport = FakeTransport()
        
        s.cmd_quit()
        self.assertEqual(called, [True])
















