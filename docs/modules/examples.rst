Example Usages
==============

Here are some ways to use our package in **your own bot!** For github based examples, see `the examples directory <https://github.com/Ext-Creators/discord-ext-ipc/tree/master/examples>`_.


A basic implementation
----------------------

The bot file:

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands, ipc


    class MyBot(commands.Bot):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.ipc = ipc.Server(self, secret_key="my_secret_key")  # create our IPC Server

        async def on_ready(self):
            """Called upon the READY event"""
            print("Bot is ready.")

        async def on_ipc_ready(self):
            """Called upon the IPC Server being ready"""
            print("Ipc is ready.")

        async def on_ipc_error(self, endpoint, error):
            """Called upon an error being raised within an IPC route"""
            print(endpoint, "raised", error)


    my_bot = MyBot(command_prefix="!", intents=discord.Intents.all())


    @my_bot.ipc.route()
    async def get_member_count(data):
        guild = my_bot.get_guild(
            data.guild_id
        )  # get the guild object using parsed guild_id

        return guild.member_count  # return the member count to the client


    if __name__ == "__main__":
        my_bot.ipc.start()  # start the IPC Server
        my_bot.run("TOKEN")

The webserver file:

.. code-block:: python
    :linenos:

    from quart import Quart
    from discord.ext import ipc


    app = Quart(__name__)
    ipc_client = ipc.Client(
        secret_key="my_secret_key"
    )  # secret_key must be the same as your server


    @app.route("/")
    async def index():
        member_count = await ipc_client.request(
            "get_member_count", guild_id=12345678
        )  # get the member count of server with ID 12345678

        return str(member_count)  # display member count


    if __name__ == "__main__":
        app.run()


Cog based IPC implementation
----------------------------

The bot file:

.. code-block:: python
    :linenos:

    import discord
    from discord.ext import commands, ipc


    class MyBot(commands.Bot):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.ipc = ipc.Server(self, secret_key="my_secret_key")  # create our IPC Server

            self.load_extension("cogs.ipc")  # load the IPC Route cog

        async def on_ready(self):
            """Called upon the READY event"""
            print("Bot is ready.")

        async def on_ipc_ready(self):
            """Called upon the IPC Server being ready"""
            print("Ipc is ready.")

        async def on_ipc_error(self, endpoint, error):
            """Called upon an error being raised within an IPC route"""
            print(endpoint, "raised", error)


    my_bot = MyBot(command_prefix="!", intents=discord.Intents.all())


    if __name__ == "__main__":
        my_bot.ipc.start()  # start the IPC Server
        my_bot.run("TOKEN")

The cog file:

.. code-block:: python
    :linenos:

    from discord.ext import commands, ipc


    class IpcRoutes(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @ipc.server.route()
        async def get_member_count(self, data):
            guild = self.bot.get_guild(
                data.guild_id
            )  # get the guild object using parsed guild_id

            return guild.member_count  # return the member count to the client


    def setup(bot):
        bot.add_cog(IpcRoutes(bot))

The webserver file:

.. code-block:: python
    :linenos:

    from quart import Quart
    from discord.ext import ipc


    app = Quart(__name__)
    ipc_client = ipc.Client(
        secret_key="my_secret_key"
    )  # secret_key must be the same as your server


    @app.route("/")
    async def index():
        member_count = await ipc_client.request(
            "get_member_count", guild_id=12345678
        )  # get the member count of server with ID 12345678

        return str(member_count)  # display member count


    if __name__ == "__main__":
        app.run()
