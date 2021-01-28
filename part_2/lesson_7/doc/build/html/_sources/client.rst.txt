Client Module documentation
=================================================

A client application for messaging. Supports
sending messages to users who are online, messages are encrypted
using the RSA algorithm with a key length of 2048 bits.

Supports command line arguments:

'python client.py {server name} {port} -N or name {username} - N or-password, {password}`

1. {server name} - the address of the message server.
2. {port} - the port on which connections are accepted
3. -n or-name-the name of the user to log in with.
4. -p or -- password-the user's password.

All command-line options are optional, but the user name and password must be paired.

Examples of usage:

* 'python client.py`

* Launch the app with the default settings.*

* 'python client.py ip_address some_port`

* Launch the application with instructions to connect to the server at ip_address: port*

* `python -n test1 -p 123`

* Launch the app with user test1 and password 123*

* 'python client.py ip_address some_port -n test1 -p 123`

* Launch the application with the user test1 and password 123 and the instruction to connect to the server at ip_address: port*

client.py
~~~~~~~~~

Run the module contains a parser for command line arguments and functionality of the application is initialized.

the client. ** arg_parser** ()
Command-line argument parser, returns a tuple of 4 elements:

* server address
* port
* user name
* The password

checks whether the port number is correct.


client_database.py
~~~~~~~~~~~~~~~~~~

.. autoclass:: client.client_database.ClientDB
    :members:

client_connection.py
~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.client_connection.Client
    :members:

client_gui.py
~~~~~~~~~~~~~~

.. autoclass:: client.client_gui.ClientMainWindow
    :members:

client_window.py
~~~~~~~~~~~~~~~~~

.. autoclass:: client.client_window.Ui_MainClientWindow
    :members:

login.py
~~~~~~~~~~~~~~~

.. autoclass:: client.login.LoginWindow
    :members:

login_reg_window.py
~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.login_reg_window.Ui_Dialog
    :members:

login_fail.py
~~~~~~~~~~~~~~~

.. autoclass:: client.login_fail.LoginWindowFail
    :members:

login_fail_window.py
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: client.login_fail_window.Ui_Dialog
    :members:

add_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.add_contact.AddContactDialog
    :members:


del_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.del_contact.DelContactDialog
    :members:

