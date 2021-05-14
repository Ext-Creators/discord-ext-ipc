from discord.ext import commands, ipc


class IpcRoutes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ipc.server.route()
    async def get_member_count(self, data):
        guild = self.bot.get_guild(data.guild_id)  # get the guild object using parsed guild_id

        return guild.member_count  # return the member count to the client


def setup(bot):
    bot.add_cog(IpcRoutes(bot))
