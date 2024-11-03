# NOTE: This requires ImageMagick installed on the device https://imagemagick.org/script/download.php
# It also needs this image template saved as 'nimitz.png' https://cdn.discordapp.com/attachments/902633836108709978/902635626665504799/nimitz.png
from config import config

import io

import wand
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color
from wand.font import Font

import discord
from discord.ext import commands


async def make_nimitz_meme(self, ctx):
    nimitzLines = ['', '', '']
    nimitzCounter = 2
    async for message in ctx.history(limit=200, before=ctx.message):
        if message.author.id == config["NIMITZ"]["ID"] and nimitzCounter >= 0 and message.content:
            nimitzLines[nimitzCounter] = message.content
            nimitzCounter -= 1
    if '' in nimitzLines or nimitzCounter > -1:
        await ctx.message.channel.send("Unfortunately, his ramblings were too cryptic for even me to parse this time.")
    else:
        with Image(filename=config["NIMITZ"]["FILE"]) as img:
            with Drawing() as draw:
                impact = wand.font.Font('impact', size=0, color='White', antialias=True)
                img.caption(nimitzLines[0], left=16, top=111, width=517, height=96, font=impact, gravity='south_west')
                img.caption(nimitzLines[1], left=16, top=551, width=517, height=96, font=impact, gravity='south_west')
                img.caption(nimitzLines[2], left=16, top=763, width=517, height=96, font=impact, gravity='south_west')
                jpeg_bin = img.make_blob('jpeg')
                await ctx.send(file=discord.File(fp=io.BytesIO(jpeg_bin), filename="nimitz.jpg"))

class NimitzCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='nimitz')
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _command_nimitz_meme(self, ctx):
        await make_nimitz_meme(self, ctx)

    @commands.Cog.listener("on_message")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _trigger_nimitz_meme(self, message):
        msg_text = message.clean_content.lower()
        if config["NIMITZ"]["TRIGGER"] in msg_text:
            ctx = await self.bot.get_context(message)
            await make_nimitz_meme(self, ctx)
           

async def setup(bot):
    await bot.add_cog(NimitzCog(bot))