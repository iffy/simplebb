Motivation
==========

    simplebb runs code on lots of machines and returns the results to a central
    server.  Simple setup is the goal.  I wrote this because I couldn't get
    Buildbot to do what I wanted.

Quick Start
===========

::

    # Get the code    
    git clone git@github.com:iffy/simplebb.git simplebb.git

    # Install dependencies
    easy_install Twisted

    # Start the simplebb server
    cd simplebb.git
    twistd -y masterd_tac.py --pidfile=master.pid

    # Create build step repo
    mkdir -p ~/.simplebb/buildscripts/

    # Create a build for the "foo" project
    cat <<EOF > ~/.simplebb/buildscripts/foo
    #!/bin/bash
    
    echo "It works"
    exit 0
    EOF
    chmod u+x ~/.simplebb/buildscripts/foo

    # Create a build for the "bar" project
    cat <<EOF > ~/.simplebb/buildscripts/bar
    #!/bin/bash
    
    branch=$1
    echo "This is broken on branch $branch"
    exit 1
    EOF
    chmod u+x ~/.simplebb/buildscripts/bar

    # Start a builder
    twistd -y clientd_tac.py --pidfile=client.pid

    # Suggest building the "foo" project's "master" branch
    PYTHONPATH=. python simplebb/suggest.py -H 127.0.0.1 foo master
    
    # Success in the server log
    cat server.log

    # Suggest building the "bar" project's "dev" branch
    PYTHONPATH=. python simplebb/suggest.py -H 127.0.0.1 bar dev

    # Failure in the server log
    cat server.log

    # See what the builder logs
    cat builder.log
    

Components
==========

    Server
    ------

    The simplebb server daemon runs on a machine somewhere that's accessible to
    all the builders.  The server doesn't need access to any of the code that's
    being built.

    Builder
    -------

    You can have as many builders as you want.  A builder is responsible for
    fetching code, building it, then reporting to the server the results of a
    build.  Builders can connect and disconnect freely.  If a builder is
    connected to the server, the builder will be informed of any builds
    suggested to the server.


Git Hook
========

    There's a sample post-receive git hook in the example/ dir.

