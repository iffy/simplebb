import inspect
import shlex

from twisted.protocols.basic import LineReceiver
from twisted.python import log
from twisted.internet.protocol import Factory



class ShellProtocol(LineReceiver):
    """
    I am the protocol used when connecting via a terminal interface.
    """
    
    _commands = None
    
    hub = None


    def showPrompt(self):
        self.transport.write('> ')


    def connectionMade(self):
        self.sendLine('Type "help" for help')
        self.showPrompt()


    def lineReceived(self, line):
        parsed = self.parseCmd(line)
        self.runCmd(*parsed)
    
    
    def dataReceived(self, data):
        LineReceiver.dataReceived(self, data)
        if data == '\x04':
            self.transport.loseConnection()


    def parseCmd(self, s):
        """
        Break this string into command tokens
        """
        return shlex.split(s)
    
    
    def getCommands(self):
        """
        Returns a dictionary of all the commands this guy supports
        """
        if self._commands is not None:
            return self._commands
        def f(x):
            if inspect.ismethod(x) or inspect.isfunction(x):
                return True
            else:
                return False
        funcs = inspect.getmembers(self, f)
        funcs = filter(lambda x:x[0].startswith('cmd_'), funcs)
        ret = {}
        for name, method in funcs:
            ret[name[len('cmd_'):]] = method
        self._commands = ret
        return ret
    
    
    def runCmd(self, cmd, *args):
        """
        Run the given command with the given args
        """
        c = self.getCommands()
        try:
            method = c[cmd]
        except KeyError, e:
            log.msg(e)
            self.sendLine('No command named %s.  Type help' % cmd)
            self.showPrompt()
            return False

        try:
            r = method(*args)
            self.showPrompt()
            return r
        except TypeError, e:
            log.msg(e)
            self.sendLine('Error trying to run command.  Type help %s' % cmd)
        except Exception, e:
            log.msg(e)
            self.sendLine('Error while running command.  Type help %s' % cmd)
            
        self.showPrompt()
        return False
    
    
    def cmd_quit(self):
        self.transport.loseConnection()
    
    
    def cmd_help(self, command=None):
        """
        Display this help (type "help help" for more help)
        
        You can get specific help for a command by typing "help" then
        the command name.  For instance:
        
            help build
            
        """
        c = self.getCommands()
        
        if command is None:
            # full help
            keys = c.keys()
            keys.sort()
            
            size = max(map(len, keys))
            r = '  %%%ss  %%s' % size
            
            self.sendLine('-'*40)
            for k in keys:
                f = c[k]
                doc = getattr(f, '__doc__', '') or ''
                doc = doc.strip().split('\n')[0].strip()
                self.sendLine(r % (k, doc))
            self.sendLine('-'*40)
        else:
            # single command
            if command not in c:
                self.sendLine('No such command: %s; type "help" for a list of commands' % command)
                return False
            
            f = c[command]
            
            # usage
            args = inspect.getargspec(f)
            names = args[0][1:]
            defaults = 0
            if args.defaults:
                defaults = len(args.defaults)
            
            args = []
            for arg in names[::-1]:
                if defaults:
                    args.append('[%s]' % arg)
                    defaults -= 1
                else:
                    args.append(arg)
            args.reverse()
            self.sendLine('-'*40)
            self.sendLine('usage: %s' % ' '.join([command] + args))
            
            # help
            doc = getattr(f, '__doc__', '') or ''
            lines = doc.split('\n')
            for line in lines:
                if line.startswith(' '*8):
                    self.sendLine(line[8:])
                else:
                    self.sendLine(line)
            self.sendLine('-'*40)


    def cmd_build(self, project, version):
        """
        Request a build.
        
        The returned hash is the request identifier.
        """
        request = dict(project=project, version=version, test_path=None)
        response = self.hub.build(request)
        self.sendLine('Build requested: %s' % response['uid'])
    
    
    def cmd_start(self, endpoint):
        """
        Start a simplebb server for other simplebb instances to connect to.
        
        Other instances can connect to this server by using the connect
        command.
        
        The only argument is a Twisted endpoint description such as:
        
            tcp:8080
                       
            ssl:443:privateKey=key.pem:certKey=crt.pem
        
        socuteurl.com/ittyfuzzy
        """
        factory = self.hub.getPBServerFactory()
        d = self.hub.startServer(factory, endpoint)
        
        def cb(_, self, endpoint):
            self.sendLine('Server started: %s' % endpoint)
        d.addCallback(cb, self, endpoint)
    
    
    def cmd_stop(self, endpoint):
        """
        Stop a simplebb server that other simplebb instance connect to.
        
        The endpoint argument is a Twisted endpoint description (the same
        thing used in the "start" command) such as:
        
            tcp:8080
            
            ssl:443:privateKey=key.pem:certKey=crt.pem

        socuteurl.com/ittyfuzzy
        """
        d = self.hub.stopServer(endpoint)
        def cb(_, self, endpoint):
            self.sendLine('Server stopped: %s' % endpoint)
        d.addCallback(cb, self, endpoint)


    def cmd_connect(self, endpoint):
        """
        Tell this simplebb instance to connect to another instance as a client.
        
        endpoint is a Twisted endpoint description such as:
        
            tcp:host=69.34.13.51:port=9876
        
        socuteurl.com/goobeygoobean
        """
        d = self.hub.connect(endpoint)
        def cb(_, self, endpoint):
            self.sendLine('Connected to %s' % endpoint)
        d.addCallback(cb, self, endpoint)



class ShellFactory(Factory):
    """
    I hook a ShellProtocol to a Hub
    """

    protocol = ShellProtocol


    def __init__(self, hub):
        self.hub = hub
    
    
    def buildProtocol(self, addr):
        """
        Builds the protocol
        """
        p = Factory.buildProtocol(self, addr)
        p.hub = self.hub
        return p







