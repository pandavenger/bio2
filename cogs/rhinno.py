from config import config, db

import pathlib
import os
import random
from pathlib import Path

import discord
from discord.ext import commands


def walk(path):
    for p in Path(path).iterdir():
        if p.is_dir():
            yield from walk(p)
            continue
        yield p.resolve()


class RhinnoCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cry')
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _post_crying_face(self, ctx):
        files = list(walk(Path(__file__).parent.parent / config["RHINNO"]["FOLDER"]))
        rfile = random.choice(files)
        show = os.path.basename(Path(rfile).parent)

        await ctx.message.channel.send("omw to beat up someone from " + show)
        async with ctx.message.channel.typing():
            await ctx.message.channel.send(file=discord.File(rfile))



def setup(bot):
    bot.add_cog(RhinnoCog(bot))
