from config import config
import random

import discord
from discord.ext import tasks, commands

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()

    def cog_unload(self):
        self.change_status.stop()

    @tasks.loop(seconds=600.0)
    async def change_status(self):
        await self.bot.change_presence(activity=discord.Game(name=random.choice(config["BOT"]["PLAYING_WITH"]), type=1, url='https://github.com/pandavenger/bio2'))


def setup(bot):
    bot.add_cog(StatusCog(bot))
