# import random, asyncio is required for discord.py
import random

# imports the required pieces from discord.py
import discord
from discord.ext import commands

# imports config file
from config import config

# import colors
from termcolor import cprint

cogs = [
        'cogs.replies',
        'cogs.sauce',
        'cogs.textgen',
        'cogs.emotes',
        'cogs.rhinno',
        'cogs.pings',
        'cogs.channels',
        'cogs.roll'
       ]

bot = commands.Bot(command_prefix=config["BOT"]["PREFIX"])

if __name__ == '__main__':
    for extension in cogs:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\n Using discord.py v{discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    await bot.change_presence(activity=discord.Game(name=random.choice(config["BOT"]["PLAYING_WITH"]), type=1, url='https://github.com/pandavenger/bio2'))
    bot.load_extension('cogs.status')

bot.run(config["BOT"]["TOKEN"], bot=True, reconnect=True)
