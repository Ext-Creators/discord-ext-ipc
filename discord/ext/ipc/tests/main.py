import discord
from discord.ext import commands
from ipc import Server

bot = commands.Bot(command_prefix="!")
ipc = Server(bot, "localhost", 8765, "my_auth_token")

@bot.event
async def on_ready():
    print("Bot ready")

@bot.event
async def on_ipc_ready():
    print("Ipc ready")

@ipc.route()
async def get_guild_count(data):
    return len(bot.guilds)

ipc.start()
bot.run("NzE3NzU1MjA3NTkyNzA2MTE4.Xte7oA.755b_z3wrop2R0kBnsrq34jOOCI")