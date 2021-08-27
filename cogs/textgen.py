from config import config
import aiohttp

import discord
from discord.ext import commands


class TextGenCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def text_gen(self, message):
        _msg_text = message.clean_content.lower()
        _response = ""

        # cannot reply to itself
        if message.author == self.bot.user:
            return

        if "top ten reasons" in _msg_text in _msg_text:
            params = {'msg': _msg_text, 'type': 2}
            async with message.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(config["TEXTGEN"]["URL"], params=params) as r:
                        _response = await r.text()

        elif "subvert" in _msg_text and "expect" in _msg_text:
            params = {'msg': "I can't believe that", 'type': 3}
            async with message.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(config["TEXTGEN"]["URL"], params=params) as r:
                        _response = await r.text()

        elif self.bot.user in message.mentions:
            _msg_text = _msg_text.replace('@bio2', '')
            _msg_text = _msg_text.replace('@bioalpha', '')
            params = {'msg': _msg_text + "\n", 'type': 1}
            async with message.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(config["TEXTGEN"]["URL"], params=params) as r:
                        _response = await r.text()

        if _response:
            _response = _response.replace("nigger", "rigger")
            _response = _response.replace("fag", "friend")
            _response = _response.replace("retard", "rhubarb")
            _response = _response.replace("cancer", "garbaggio")
            _response = _response.replace("nigger", "rigger")

            try:
                await message.channel.send(_response)
            except Exception as e:
                print(e)
                await message.channel.send(config["BOT"]["ERROR_MESSAGE"])


def setup(bot):
    bot.add_cog(TextGenCog(bot))
