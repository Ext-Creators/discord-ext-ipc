### discord-ext-ipc

An IPC extension allowing for the communication between a [discord.py](https://discordpy.readthedocs.io/en/latest/) bot and an asynchronous web-framework (i.e. [Quart](https://pgjones.gitlab.io/quart/) or [aiohttp.web](https://docs.aiohttp.org/en/stable/web_quickstart.html))

## Installing

As with other extensions, instillation is through [git](https://git-scm.com)

```py
python -m pip install -U git+https://github.com/lganwebb/discord-ext-ipc
```

## Basic Usage / Getting started

One of the most basic programs you can make is a simple guild counter web-page. An example using [Quart](https://pgjones.gitlab.io/quart/):

```py
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
```

```py
# WEB SERVER FILE
from quart import Quart
from discord.ext.ipc import Client

app = Quart(__name__)
web_ipc = Client("localhost", 8765, "secret_key")

@app.route("/")
async def show_guilds():
    guild_count = await web_ipc.request("get_guild_count") # Make a request to get the bot's IPC get_guild_count route.

    return guild_count # return the data sent to us.

if __name__ == "__main__":
    app.run()
```