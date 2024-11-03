from config import config
import asyncio

import requests
import urllib.parse

import discord
from discord.ext import commands

from pysaucenao import AnimeSource, MangaSource, BooruSource, SauceNao


class SauceCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.saucenao = SauceNao(
            api_key=config["SAUCENAO"]["KEY"],
            min_similarity=70.0,
            priority=[21, 22, 5]
        )

    @commands.Cog.listener("on_raw_reaction_add")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def get_sauce(self, payload):

        if payload.emoji.name != config["REACTS"]["SAUCE"]:
            return

        _message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        _results = []
        _traceresults = []
        _original = []
        if len(_message.attachments) > 0:
            for embed in _message.embeds:
                _original.append(embed.url)
                try:
                    _result = await self.saucenao.from_url(embed.url)
                    if _result.short_remaining <= 0:
                        await asyncio.sleep(30)

                except Exception as e:
                    print(e)
                    _result = False

                if _result is False or _result.count == 0:
                    _result = requests.get("https://api.trace.moe/search?anilistInfo&url={}".format(
                        urllib.parse.quote_plus(embed.url))).json()
                    _traceresults.append(_result)
                    break

                _results.append(_result)

        if len(_message.embeds) > 0:
            for embed in _message.embeds:
                _original.append(embed.url)
                try:
                    _result = await self.saucenao.from_url(embed.url)
                    if _result.short_remaining <= 0:
                        await asyncio.sleep(30)

                except Exception as e:
                    print(e)
                    _result = False

                if _result is False or _result.count == 0:
                    _result = requests.get("https://api.trace.moe/search?anilistInfo&url={}".format(
                        urllib.parse.quote_plus(embed.url))).json()
                    _traceresults.append(_result)
                    break

        for r in _traceresults:
            result = r['result'][0]

            # print(result)

            _thumbnail = result['image']
            _url = result['video']
            _similarity = result['similarity']
            _title = result['filename']
            _episode = result['episode']
            _timestamp = f'{result["from"]}s - {result["to"]}s'

            _colour = discord.Colour(0xb8e986)
            _embed = discord.Embed(colour=_colour)
            _embed.set_thumbnail(url=_thumbnail)

            if _similarity:
                _embed.add_field(name="Similarity", value=str(_similarity))
            if _title:
                if isinstance(result, BooruSource):
                    _embed.add_field(name="Major Tags", value=str(_title))
                else:
                    _embed.add_field(name="Title", value=str(_title))
            if _episode != -1:
                _embed.add_field(name="Episode", value=str(_episode))
            if _timestamp:
                _embed.add_field(name="Timestamp", value=str(_timestamp))
            if _url:
                # _url = f'[{_url}]({_url})'
                _embed.add_field(name="Video", value=_url, inline=False)
                # _embed.__setattr__('url', _url)

            try:
                await _message.channel.send(embed=_embed)
            except Exception as e:
                print(e)

        i = 0
        lasturl = ""
        for r in _results:

            _thumbnail = _original[i]
            _description = ""
            _url = ""
            _similarity = ""
            _title = ""
            _author = ""
            _chapter = -883
            _episode = -1
            _timestamp = ''

            if not r:
                _description = "What do I look like to you, a bot? Look it up yourself."
                _colour = discord.Colour(0xd0021b)
            else:
                _colour = discord.Colour(0xb8e986)
                result = r[0]
                _similarity = result.similarity
                _title = result.title

                if isinstance(result, AnimeSource):
                    await result.load_ids()

                    _url = ""
                    if result.anilist_url is not None:
                        _url = result.anilist_url
                    elif result.mal_url is not None:
                        _url = result.mal_url
                    elif result.anidb_url is not None:
                        _url = result.anidb_url
                    else:
                        _url = result.url
                    if result.episode is not None:
                        _episode = result.episode
                    if result.timestamp is not None:
                        timestamp = result.timestamp
                elif isinstance(result, MangaSource):
                    if not result.url:
                        _url = ""
                    else:
                        if not result.chapter:
                            _url = result.url
                        else:
                            _url = result.url
                            _chapter = result.chapter
                else:
                    _author = result.author_name
                    if not result.source_url:
                        _url = ""
                    else:
                        _url = result.source_url

            _embed = discord.Embed(colour=_colour,
                                   description=_description)
            _embed.set_thumbnail(url=_thumbnail)

            if _similarity:
                _embed.add_field(name="Similarity", value=str(_similarity))
            if _title:
                if isinstance(result, BooruSource):
                    _embed.add_field(name="Major Tags", value=str(_title))
                else:
                    _embed.add_field(name="Title", value=str(_title))
            if _episode != -1:
                _embed.add_field(name="Episode", value=str(_episode))
            if _timestamp:
                _embed.add_field(name="Timestamp", value=str(_timestamp))
            if _chapter != -883:
                _embed.add_field(name="Chapter", value=str(_chapter))
            if _author:
                _embed.add_field(name="Author", value=str(_author))
            if _url:
                # _url = f'[{_url}]({_url})'
                _embed.add_field(name="Source", value=_url, inline=False)
                # _embed.__setattr__('url', _url)

            try:
                if lasturl == _url:
                    await _message.channel.send(embed=_embed)
                    _url = lasturl
            except Exception as e:
                print(e)

            i += 1


async def setup(bot):
    await bot.add_cog(SauceCog(bot))
