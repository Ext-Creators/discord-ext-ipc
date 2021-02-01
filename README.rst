.. raw:: html

    <p align="center">
        <a href="https://github.com/Ext-Creators/discord-ext-ipc/actions?query=workflow%3AAnalyze+event%3Apush">
            <img alt="Analyze Status"
                 src="https://github.com/Ext-Creators/discord-ext-ipc/workflows/Analyze/badge.svg?event=push" />
        </a>

        <a href="https://github.com/Ext-Creators/discord-ext-ipc/actions?query=workflow%3ABuild+event%3Apush">
            <img alt="Build Status"
                 src="https://github.com/Ext-Creators/discord-ext-ipc/workflows/Build/badge.svg?event=push" />
        </a>

        <a href="https://github.com/Ext-Creators/discord-ext-ipc/actions?query=workflow%3ALint+event%3Apush">
            <img alt="Lint Status"
                 src="https://github.com/Ext-Creators/discord-ext-ipc/workflows/Lint/badge.svg?event=push" />
        </a>
    </p>

----------

.. raw:: html

    <h1 align="center">discord-ext-ipc</h1>
    <p align="center">A discord.py extension for inter-process communication.</p>


Installation
------------

.. code-block:: sh

    # Windows
    py -3 -m pip install --upgrade discord-ext-ipc

    # Linux
    python3 -m pip install --upgrade discord-ext-ipc


Usage
-----

For examples using Quart, refer to `the examples directory <https://github.com/Ext-Creators/discord-ext-ipc/tree/master/examples>`_.


Running
-------

To run the IPC Server, simply run your bot as normal. Once the `on_ipc_ready` event has been dispatched, run your webserver.

For support join the `Ext-Creators Discord Server <https://discord.gg/h3q42Er>`_.
