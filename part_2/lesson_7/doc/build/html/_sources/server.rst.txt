Server Module
=================================================

The messenger server module. Processes dictionaries message, stores the public keys of the clients.

Using

The module holds the arguments of the command line:

1. -p - Port on which connections are accepted
2. -a - The address from which connections are received.

Usage examples:

'python server.py -p 8080`

* Starting the server on port 8080*

'python server.py -local host`

* Starting a server that accepts only connections to localhost*


server.py
~~~~~~~~~

Run the module contains a parser for command line arguments and functionality of the application is initialized.

server. ** arg_parser** ()
Command-line argument parser, returns a tuple of 4 elements:

* the address from which to accept connections
* port


server_database.py
~~~~~~~~~~~~~~~~~~~

.. autoclass:: server.server_database.ServerDB
    :members:

server_gui.py
~~~~~~~~~~~~~~

.. autoclass:: server.server_gui.MainGui
    :members:

.. autoclass:: server.server_gui.HistoryWindow
    :members:

.. autoclass:: server.server_gui.ConfigWindow
    :members:

