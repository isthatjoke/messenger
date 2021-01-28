Additionals package
=================================================

A package of common utilities used in different modules of the project.

Script decos.py
---------------

.. automodule:: additionals.decos
    :members:

Script client_descriptor.py
---------------------------

.. autoclass:: additionals.client_descriptor.PortVerifier
    :members:

.. autoclass:: additionals.client_descriptor.HostVerifier
    :members:

Script server_descriptor.py
---------------------------

.. autoclass:: additionals.server_descriptor.PortVerifier
    :members:

.. autoclass:: additionals.server_descriptor.HostVerifier
    :members:

Script check_ip.py
---------------------

.. automodule:: additionals.check_ip
    :members:

Script errors.py
---------------------

.. autoclass:: additionals.errors.IncorrectData
    :members:

.. autoclass:: additionals.errors.IncorrectType
    :members:

.. autoclass:: additionals.errors.IncorrectDataToDecode
    :members:

.. autoclass:: additionals.errors.ClientError
    :members:

Script client_meta.py
-----------------------

.. autoclass:: additionals.client_meta.ClientVerifier
    :members:

Script server_meta.py
-----------------------

.. autoclass:: additionals.server_meta.ServerVerifier
    :members:

Script utils.py
---------------------

additionals.utils. **receive_msg** (sender)


Function for receiving messages from remote computers. Accepts JSON messages,
decodes the received message, and verifies that the dictionary is received.

additionals.utils. **send_msg** (sock, message)


Function for sending dictionaries via socket. Encodes the dictionary in JSON format and sends it via a socket.


Script settings.py
---------------------

Contains different global variables of the project.