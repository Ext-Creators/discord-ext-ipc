import discord
from discord.ext import commands, ipc

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ipc = ipc.Server(self, "localhost", 8765, "my_secret_key") # create our IPC Server

        self.load_extension("cogs.ipc") # load the IPC Route cog
    
    async def on_ready(self):
        """Called upon the READY event"""
        print("Bot is ready.")
    
    async def on_ipc_ready(self):
        """Called upon the IPC Server being ready"""
        print("Ipc is ready.")

my_bot = MyBot(command_prefix="!", intents=discord.Intents.all())

if __name__ == "__main__":
    my_bot.ipc.start() # start the IPC Server
    my_bot.run("TOKEN")