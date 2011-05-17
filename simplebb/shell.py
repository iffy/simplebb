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
    
    
    def cmd_build(self, project, version, test=None):
        """
        Request a build.
        """
        self.factory.brain.buildProject(project, version, test)



