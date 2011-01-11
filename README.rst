========
simplebb
========


simplebb runs code on lots of machines and returns the results to a central
server.  Simple setup is the goal.  I wrote this because I couldn't get
Buildbot to do what I wanted.


Quick Start
===========

Get the code::

    git clone git@github.com:iffy/simplebb.git simplebb.git
    
Install dependencies::

    easy_install Twisted
    
Start the `simplebb` server::
    
    cd simplebb.git
    twistd -y masterd_tac.py --pidfile=master.pid
    
Create build step directory::

    mkdir -p ~/.simplebb/buildscripts/

Create build steps for the `foo` project::

    cat <<EOF > ~/.simplebb/buildscripts/foo
    #!/bin/bash
    echo "It works"
    exit 0
    EOF
    chmod u+x ~/.simplebb/buildscripts/foo

Create build steps for the `bar` project::

    cat <<EOF > ~/.simplebb/buildscripts/bar
    #!/bin/bash    
    branch=$1
    echo "This is broken on branch $branch"
    exit 1
    EOF
    chmod u+x ~/.simplebb/buildscripts/bar

Start a builder::

    twistd -y clientd_tac.py --pidfile=client.pid

Suggest building the `foo` project's `master` branch::

    PYTHONPATH=. python simplebb/suggest.py -H 127.0.0.1 foo master

Success in the server log::

    cat server.log

Suggest building the `bar` project's `dev` branch::

    PYTHONPATH=. python simplebb/suggest.py -H 127.0.0.1 bar dev

Failure in the server log::

    cat server.log

See what the builder logs::

    cat builder.log
    

Components
==========

Server
------

The `simplebb` server daemon runs on a machine accesible to the builders.  The
server doesn't need access to any of the code that's being built.

To start a build on all builders connected to the server, you *suggest* a build
by means of the `simplebb/suggest.py` script.  The server passes the suggestion
on to all the builders (who can do what they want with the suggestion).

The server needs no prior knowledge of which projects are going to be built: he
accepts any build reports for any projects from any number of builders.
Currently, all build responses are only shown in the server log -- maybe a web
interface will materialize... maybe not.

Builder
-------

A `simplebb` builder daemon connects to a `simplebb` server (TCP) and
waits for the server to suggest the building of a project.  Projects are
identified by the name of build step file (in `~/.simplebb/buildscripts/`).

If the server asks a builder to build an unknown project, the builder fails with
a response of -1.  I might make the builders ignore the request in the future.

The builder is responsible for fetching the code to be built, knowing how to build
it, building the code and telling the server how a build went.  When the builder
sends a build report to the server, additional information about the machine
is sent to the server (`os.uname()` and `sys.version`).


Git Hook
========

There's a sample post-receive git hook in the example/ dir.

