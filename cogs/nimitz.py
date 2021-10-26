# NOTE: This requires ImageMagick installed on the device https://imagemagick.org/script/download.php
# It also needs this image template saved as 'nimitz.png' https://cdn.discordapp.com/attachments/902633836108709978/902635626665504799/nimitz.png

from config import config, db

import Wand
from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color
from wand.font import Font

import discord
from discord.ext import commands


class NimitzCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='nimitz')
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _make_nimitz_meme(ctx):
        NimitzLines = ['','','']
        NimitzCounter = 2
        async for message in ctx.history(limit=200,before=ctx.message):
            if message.author.id == 208427860560445441 and counter >= 0:
                NimitzLines[NimitzCounter] = message.content
                NimitzCounter -= 1
        if '' in NimitzLines:
            ctx.send("Failed to make fun of nimitz.")
        else:
            with Image(filename='nimitz.png') as img:
                with Drawing() as draw:
                    NimitzFont = wand.font.Font('impact', size=0, color='White', antialias=True)
                    img.caption(NimitzLines[0], left=16, top=111, width=517, height=96, font=memetext, gravity='south_west')
                    img.caption(NimitzLines[1], left=16, top=551, width=517, height=96, font=memetext, gravity='south_west')
                    img.caption(NimitzLines[2], left=16, top=763, width=517, height=96, font=memetext, gravity='south_west')
                    img.save(filename='output.png')
                await ctx.send(file=discord.File('output.png'))
           
            
            
def setup(bot):
    bot.add_cog(NimitzCog(bot))
    