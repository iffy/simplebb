from zope.interface import Interface, Attribute



class IBuild(Interface):
    """
    I am a single Build of a single project of a single version.
    """


    done = Attribute('''
        Deferred that fires with self once the build is done.
        ''')


    uid = Attribute('''
        str: unique identifier for this Build
        ''')
    
    
    status = Attribute('''
        int: status indicating success (0) or failure (non-0) of Build.
        
        None if Build is not yet finished
        ''')
    
    
    version = Attribute('''
        str: version passed to the underlying build steps.
        ''')
    
    
    project = Attribute('''
        str: name of project being built.
        ''')

    
    test_path = Attribute('''
        str: name of specific build steps used.
        
        Often '', otherwise a 'path/of/this/form'
        ''')

    builder = Attribute('''
        IBuilder: the owner of this Build.
        ''')

    
    runtime = Attribute('''
        int: number of seconds it took to run this Build.
        ''')


    def run():
        """
        Run this build.
        
        Returns self.done Deferred.
        """



class IBuilder(Interface):
    """
    I am something that responds to build requests by creating Builds.
    """
    
    name = Attribute('''
        str: name of this Builder
        ''')

    
    uid = Attribute('''
        str: unique identifier for this Builder
        ''')
    
    
    builds = Attribute('''
        list[IBuild]: builds I know about that have not finished.
        ''')


    def requestBuild(version, project, test_path=None):
        """
        Request that I build the given project for the given version.
        
        Returns a Deferred that fires with a list of Builds.
        """
    
    
    def addReporter(reporter):
        """
        Add a reporter to this Builder.
        
        Reporters are callables that are called when something interesting happens
        to a Build.  Right now, interesting events are creation and completion.
        """
    
    
    def removeReporter(reporter):
        """
        Remove a reporter from this Builder.
        """



