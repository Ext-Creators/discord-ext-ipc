discord-ext-ipc
===============

An IPC extension allowing for the communication between a discord.py bot and an asynchronous web-framework (i.e. Quart or aiohttp.web)

Installation
------------

Installation can be complete through github only:

.. code-block:: sh

    python -m pip install -U git+https://github.com/ext-creators/discord-ext-ipc


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

To run the IPC Server, simply run your bot as normal. Once the `on_ipc_readu` event has been dispatched, run your webserver.

For support join the `Ext-Creators Discord Server <https://discord.gg/h3q42Er>`_.
