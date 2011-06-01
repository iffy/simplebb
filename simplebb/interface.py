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



class IBuilder(Interface):
    """
    I am something that responds to build requests.
    """
    
    name = Attribute('''
        str: name of this Builder
        ''')

    
    uid = Attribute('''
        str: unique identifier for this Builder
        ''')


    def requestBuild(project, version, test_path=None, reqid=None):
        """
        Request that I build the given project for the given version.
        """



class IReporter(Interface):
    """
    I accept notification about builds via my L{report} method.
    """
    
    
    def buildReceived(buildDict):
        """
        Called with a Build dictionary whenever something interesting happens.
        """
    
    
    def addReporter(reporter):
        """
        Chain a reporter to this reporter.
        """
    
    
    def removeReporter(reporter):
        """
        Remove a reporter from this reporter's chain.
        """



class IBuilderHub(Interface):
    """
    I hold many Builders 
    """

    
    def addBuilder(builder):
        """
        Add a builder to this builder chain.
        """
    
    
    def removeBuilder(builder):
        """
        Remove a builder from this builder chain.
        """


