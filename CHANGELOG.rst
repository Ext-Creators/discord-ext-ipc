Changelog
=========

1.1.0a
------

- Added **discord.ext.ipc.client.Client(...).discover()**: Returns a Node connection to your IPC server, allowing for easier communication.
- Completely changed **discord.ext.ipc.client.Client(...)** to a Node based system, see README.md for new structure.

1.1.1a
------

- Fixed import errors

1.1.2a
------

- **discord.ext.ipc.client.Node(...).request(...)** now returns None if 'null' is received.

1.1.3a
------

- The library will now close the writer object.
- The library will read until EOF
