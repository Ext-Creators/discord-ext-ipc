Server Setup
============

The IPC server is what runs on your bot’s process.
It will run within the same loop as your bot without interfering with your bot’s process.

The server handles multiple things:

- Routes
    - These routes / endpoints are available to the client and are what your server returns upon requests being made to it.
- Authentication
    - The IPC client and server use a secret key authentication system. If your server secret key and the request’s authentication header don’t match, the request will not be carried out.
- Multicasting
    - You do not have to specify a port on your client process, only an IP (defaults to localhost). If you do not specify an IP then the client will connect to another server running on port 20000. This will return the port of your main server for the client to connect to.


So, how does it work?
The server is simply just a websocket server.
Requests are sent in a JSON payload to and from the server.
For example, a client request could be {'endpoint': 'get_guild_count', 'headers': {...}}.
This JSON is processed upon a request being made, and checks for a registered route matching the name of the endpoint supplied.
It then calls the method linked to said route and returns the payload to the client.

.. currentmodule:: discord.ext.ipc.server

.. autofunction:: route

.. autoclass:: Server
    :members:
