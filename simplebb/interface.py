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


    def requestBuild(version, name):
        """
        Request that I build the given project for the given version.
        """

    
    def listBuilds():
        """
        Returns a Deferred that fires with the list of known Builds.
        """



class IReporter(Interface):
    """
    I report the completion of a Build.
    
    Possible subclasses might include reporters that email,
    record in a database, send a text, tweet, respond to an AJAX request, etc...
    """


    def monitorBuild(build):
        """
        Monitors the Build's done Deferred with buildFinished.
        """


    def buildFinished(build):
        """
        Called once a Build completes.
        """



