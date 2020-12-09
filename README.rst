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

One of the most basic programs you can make is a simple guild counter web-page. An example using Quart:

.. code-block:: py

    # BOT FILE
    import discord
    from discord.ext import commands

    # Our bot will be the server we make requests to in order to get data from it.
    from discord.ext.ipc import Server

    class Bot(commands.Bot):
        """Main bot class"""
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        async def on_ipc_ready(self):
            """Event dispatched upon the IPC being ready"""
            print("IPC ready")

        async def on_ready(self):
            """Event dispatched upon our discord bot being ready"""
            print("Bot ready")

    bot = Bot(command_prefix="!", case_insensitive=True)
    bot_ipc = Server(bot, "localhost", 8765, "secret_key")

    # ipc.server.Server takes four arguments: the bot object, the port to run the IPC on, and a secret key used to authenticate client connections (seen in the web server file).

    @bot_ipc.route() # if no name is supplied in ipc.server.Server.route, the function name will become the route name.
    async def get_guild_count(data):
        """This route named get_guild_count will return the amount of guilds our bot is in"""
        return len(bot.guilds)

    if __name__ == "__main__":
        bot_ipc.start() # ipc.server.Server.start will begin the IPC
        bot.run("TOKEN") # run the bot as usual


.. code-block:: py

    # WEB SERVER FILE
    from quart import Quart
    from discord.ext.ipc import Client

    app = Quart(__name__)
    web_ipc = Client(secret_key="my_auth_token")

    @app.route("/")
    async def show_guilds():
        guild_count = await app.ipc_node.request("get_guild_count") # Make a request to get the bot's IPC get_guild_count route.

        return str(guild_count) # return the data sent to us.

    @app.before_first_request
    async def before():
        app.ipc_node = await web_ipc.discover() # discover IPC Servers on your network

    if __name__ == "__main__":
        app.run()

Running
-------

To run the IPC Server, simply run your bot as normal. Once the `on_ipc_ready` event has been dispatched, run your webserver.

For support join the `Ext-Creators Discord Server <https://discord.gg/h3q42Er>`_.
