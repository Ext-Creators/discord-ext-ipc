Client Connection
=================

The IPC client is very simple.
It will simply connect to your server process and send JSON data.
If you do not supply a port on initialisation, the client will connect to the multicast server
(see the server section) and return the port from said server.
If you do supply a port, it will connect to the server instantly.

Requests are made by calling ``ipc.client.request(endpoint, **kwargs)``
and will be sent to the server in the json format specified above.
It will then wait for a response and return the data.

.. currentmodule:: discord.ext.ipc.client

.. autoclass:: Client
    :members:
