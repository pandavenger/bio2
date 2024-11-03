# import random, asyncio is required for discord.py
import random
import os
import asyncio

# imports the required pieces from discord.py
import discord
from discord.ext import commands

# imports config file
from config import config

# import colors
from termcolor import cprint

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=config["BOT"]["PREFIX"], intents=intents)

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\n Using discord.py v{discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    await bot.change_presence(activity=discord.Game(name=random.choice(config["BOT"]["PLAYING_WITH"]), type=1, url='https://github.com/pandavenger/bio2'))
    await bot.load_extension('cogs.status')

@bot.command()
@commands.is_owner()
async def post(ctx, channel_id, post):
    channel = ctx.bot.get_channel(int(channel_id))
    await channel.send(post)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(config["BOT"]["TEST_TOKEN"])

asyncio.run(main())
