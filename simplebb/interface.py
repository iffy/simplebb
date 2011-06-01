from zope.interface import Interface, Attribute



class IBuild(Interface):
    """
    I am a single Build of a single project of a single version.
    """


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


    runtime = Attribute('''
        int: number of seconds it took to run this Build.
        ''')
    
    
    def toDict():
        """
        Convert this Build into a transportable dict.
        """



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



class IEmitter(Interface):
    """
    I emit build notifications to my registered observers.
    """
    
    
    def addObserver(observer):
        """
        Register an observer to be notified by this emitter.
        """
    
    
    def removeObserver(observer):
        """
        Unregister an observer from being notified by this emitter.
        """



class IObserver(Interface):
    """
    I observe interesting notifications about builds.
    """
    
    def buildReceived(buildDict):
        """
        Called with a Build dictionary.
        """



class IBuilderBoss(Interface):
    """
    I know about other Builders.
    """

    
    def addBuilder(builder):
        """
        Add a builder to this builder chain.
        """
    
    
    def removeBuilder(builder):
        """
        Remove a builder from this builder chain.
        """


