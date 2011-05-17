import inspect
import shlex

from twisted.protocols.basic import LineReceiver




class ShellProtocol(LineReceiver):
    """
    I am the protocol used when connecting via a terminal interface.
    """
    
    _commands = None


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
            return c[cmd](*args)
        except KeyError, e:
            self.sendLine('No command named %s.  Type help' % cmd)
            return False
        except TypeError, e:
            self.sendLine('Error trying to run command.  Type help %s' % cmd)
            return False
        except Exception, e:
            self.sendLine('Error while running command.  Type help %s' % cmd)
            return False
    
    
    def cmd_build(self, project, version, test=None):
        """
        Request a build.
        """
        self.factory.brain.buildProject(project, version, test)
    
    
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
            r = '%%%ss  %%s' % size
            
            for k in keys:
                f = c[k]
                doc = getattr(f, '__doc__', '')
                doc = doc.strip().split('\n')[0].strip()
                self.sendLine(r % (k, doc))
        else:
            # single command
            if command not in c:
                self.sendLine('No such command: %s; type "help" for a list of commands' % command)
                return False
            
            f = c[command]
            
            # usage
            args = inspect.getargspec(f)
            names = args[0][1:]
            defaults = len(args.defaults)
            
            args = []
            for arg in names[::-1]:
                if defaults:
                    args.append('[%s]' % arg)
                    defaults -= 1
                else:
                    args.append(arg)
            args.reverse()
            self.sendLine('usage: %s' % ' '.join([command] + args))
            
            # help
            doc = getattr(f, '__doc__', '')
            lines = doc.split('\n')
            for line in lines:
                if line.startswith(' '*8):
                    self.sendLine(line[8:])
                else:
                    self.sendLine(line)



