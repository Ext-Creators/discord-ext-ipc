from quart import Quart
from discord.ext.ipc import Client

app = Quart(__name__)
ipc = Client("localhost", 8765, "my_auth_token")

@app.route("/")
async def index():
    data = await ipc.request("get_guild_count")
    return data

app.run()