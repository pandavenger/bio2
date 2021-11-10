# NOTE: This requires ImageMagick installed on the device https://imagemagick.org/script/download.php
# It also needs these two images:
# https://cdn.discordapp.com/attachments/745357907692093505/907794897627660288/jessie.png
# https://cdn.discordapp.com/attachments/745357907692093505/907795010911625216/circle.png

from config import config, db

from wand.drawing import Drawing
from wand.image import Image
from wand.color import Color
from wand.font import Font
from urllib.request import Request,urlopen

import discord
from discord.ext import commands


class NimitzCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name='nimitz')
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _make_nimitz_meme(ctx,arg):
        if arg == 'Nimitz':
            Jessie = 'Nimitz#9070'
        else:
            Jessie = arg
        NimitzLines = ['','','']
        NimitzCounter = 2
        async for message in ctx.history(limit=200,before=ctx.message):
            if str(message.author) == Jessie and counter >= 0:
                NimitzLines[NimitzCounter] = message.content
                JessieUser = message.author
                JessieName = JessieUser.display_name
                NimitzCounter -= 1
        if '' in NimitzLines:
            ctx.send("Failed to fetch last 3 messages of",Jessie)
        else:
            JessieRequest = Request(JessieUser.avatar_url,headers={'User-Agent': 'Mozilla/5.0'})
            JessieAv = urlopen(JessieRequest).read()
            with Image(filename='jessie.png') as img:
                with Image(blob=jessie_av) as av:
                    av.resize(90,90)
                    av.save(filename='output.png')
                    av.alpha_channel = True
                    with Drawing() as draw:
                        draw.alpha(90,90,'floodfill')
                    with Image(filename='circle.png') as circle:
                        av.composite_channel(channel='alpha',image=circle,operator='replace')
                        av.save(filename='output.png')
                    with Drawing() as draw:
                        memetext = Font('impact', size=0, color='White', antialias=True)
                        img.caption(NimitzLines[0], left=16, top=111, width=517, height=96, font=memetext, gravity='south_west')
                        img.caption(NimitzLines[1], left=16, top=551, width=517, height=96, font=memetext, gravity='south_west')
                        img.caption(NimitzLines[2], left=16, top=763, width=517, height=96, font=memetext, gravity='south_west')
                        img.caption(JessieName+' what the fuck are you talking about?', left=254, top=998, width=293, height=67, font=memetext, gravity='south_west')
                        img.composite(av, left=82, top=3)
                        img.composite(av, left=122, top=460)
                        img.composite(av, left=113, top=664)
                        img.save(filename='output.png')
                    await ctx.send(file=discord.File('output.png'))
            
def setup(bot):
    bot.add_cog(NimitzCog(bot))