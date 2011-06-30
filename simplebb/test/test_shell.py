from twisted.trial.unittest import TestCase
from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from twisted.internet import defer

from zope.interface.verify import verifyClass


from simplebb.hub import Hub
from simplebb.shell import ShellProtocol, ShellFactory
from simplebb.interface import IObserver



class ShellFactoryTest(TestCase):


    def test_hub(self):
        """
        Should accept a hub
        """
        f = ShellFactory('foo')
        self.assertEqual(f.hub, 'foo')


    def test_Factory(self):
        self.assertTrue(issubclass(ShellFactory, Factory))
    
    
    def test_protocol(self):
        self.assertEqual(ShellFactory.protocol, ShellProtocol)

    
    def test_buildProtocol(self):
        """
        Should pass the hub along
        """
        f = ShellFactory('hub')
        p = f.buildProtocol('whatever')
        self.assertEqual(p.hub, 'hub')
        


class ShellProtocolTest(TestCase):
    
    
    def setUp(self):
        self.s = ShellProtocol()
    
    
    def test_lineReceiver(self):
        """
        Should be a LineReceiver
        """
        self.assertTrue(issubclass(ShellProtocol, LineReceiver))
    
    
    def test_Observer(self):
        """
        Should be an observer
        """
        verifyClass(IObserver, ShellProtocol)

    
    def test_attrs(self):
        """
        A ShellProtocol should know about some things
        """
        self.assertEqual(self.s.hub, None)

    
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


    def test_watchRequest(self):
        """
        You should be able to watch request info.
        """
        s = ShellProtocol()
        s.watchRequest('abcdef')
        self.assertEqual(s.watching, ['abcdef'])


    def test_noteReceived(self):
        """
        If the user previously called watchRequest with the given request id,
        send it to the user.
        """
        s = ShellProtocol()
        s.watching = ['abcdef']
        called = []
        s.sendLine = called.append
        
        note = {'build': {
            'req_uid': 'abcdef',
            'uid':'build-ABCDEFGHijklmnopq'
        }, 'note': 'Some note'}
        
        s.noteReceived(note)
        self.assertEqual(len(called), 1)
        self.assertTrue('Some note' in called[0])
        self.assertTrue('ABCDEFGH' in called[0], 'Should identify the build')


    def test_noteReceived_nowatch(self):
        """
        If not watching anything, don't sent anything.
        """
        s = ShellProtocol()
        called = []
        s.sendLine = called.append
        
        note = {'build': {'req_uid': 'abcdef'}, 'note':'foo'}
        
        s.noteReceived(note)
        self.assertEqual(len(called), 0) 


    def test_connectionMade(self):
        """
        Should observe the hub
        """
        s = ShellProtocol()
        s.sendLine = lambda x: None
        s.showPrompt = lambda: None
        s.hub = Hub()
        called = []
        s.hub.addObserver = called.append
        s.connectionMade()
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], s)


    def test_connectionLost(self):
        """
        Should stop observing the Hub
        """
        s = ShellProtocol()
        s.hub = Hub()
        called = []
        s.hub.remObserver = called.append
        s.connectionLost('foo')
        self.assertEqual(called, [s], "Should call remObserver on the hub")
        
        


class FakeHub:


    def __init__(self, **returns):
        self.called = []
        self.returns = returns


    def build(self, what):
        self.called.append(('build', what))
        return self.returns.get('build', None)
    
    
    def getPBServerFactory(self):
        self.called.append('getPBServerFactory')
        return self.returns.get('getPBServerFactory', None)
    
    
    def startServer(self, factory, description):
        self.called.append(('startServer', factory, description))
        return self.returns.get('startServer', None)
    
    
    def stopServer(self, description):
        self.called.append(('stopServer', description))
        return self.returns.get('stopServer', None)
    
    
    def connect(self, description):
        self.called.append(('connect', description))
        return self.returns.get('connect', None)


    def disconnect(self, description):
        self.called.append(('disconnect', description))
        return self.returns.get('disconnect', None)

        


class CommandsTest(TestCase):
    """
    I test specific commands
    """
    
    def test_build(self):
        s = ShellProtocol()
        build_response = {'uid': 'something'}
        s.hub = FakeHub(build=build_response)
        sendLine_called = []
        s.sendLine = sendLine_called.append
        
        s.cmd_build('project', 'version')
        
        self.assertEqual(sendLine_called, [],
            "Should not have sent something back")
        self.assertEqual(s.hub.called, [
            ('build', dict(project='project', version='version',
                test_path=None)),
        ])
        self.assertEqual(s.watching, ['something'])


    def test_start(self):
        """
        start should go through to startServer
        """
        shell = ShellProtocol()
        factory = object()
        server = defer.Deferred()
        shell.hub = FakeHub(getPBServerFactory=factory, startServer=server)
        sendLine = []
        shell.sendLine = sendLine.append
        
        shell.cmd_start('tcp:8080')
        
        while sendLine:
            sendLine.pop()
        self.assertIn(('startServer', factory, 'tcp:8080'), shell.hub.called)
        
        server.callback('foo')
        self.assertNotEqual(sendLine, [], "Once server starts, connectee "
                            "should be notified.")


    def test_stop(self):
        """
        stop should go through to stopServer
        """
        shell = ShellProtocol()
        stop_d = defer.Deferred()
        shell.hub = FakeHub(stopServer=stop_d)
        sendLine = []
        shell.sendLine = sendLine.append
        
        shell.cmd_stop('tcp:8080')
        
        while sendLine:
            sendLine.pop()
        self.assertIn(('stopServer', 'tcp:8080'), shell.hub.called)
        
        stop_d.callback('foo')
        self.assertNotEqual(sendLine, [], "Once server stops, connectee "
                            "should be notified.")


    def test_connect(self):
        """
        should go through to hub.connect
        """
        shell = ShellProtocol()
        client = defer.Deferred()
        shell.hub = FakeHub(connect=client)
        sendLine = []
        shell.sendLine = sendLine.append
        
        shell.cmd_connect('my endpoint')
        
        while sendLine:
            sendLine.pop()
        self.assertIn(('connect', 'my endpoint'), shell.hub.called)
        
        client.callback('foo')
        self.assertNotEqual(sendLine, [], "Once client connects, connectee "
                            "should be notified.")


    def test_disconnect(self):
        """
        should go through to hub.disconnect
        """
        shell = ShellProtocol()
        stop_d = defer.Deferred()
        shell.hub = FakeHub(disconnect=stop_d)
        sendLine = []
        shell.sendLine = sendLine.append
        
        shell.cmd_disconnect('tcp:8080')
    
        self.assertIn(('disconnect', 'tcp:8080'), shell.hub.called)










