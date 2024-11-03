from config import config, db
import re

import discord
from discord import Embed, Emoji
from discord.ext import commands


class EmotesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild = config["BOT"]["PRIMARY_GUILD"]

    def get_emote_count_all(self):
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM emotes WHERE discord_id IS NOT NULL ORDER BY count DESC")
            return cur.fetchall()
        except:
            return None

    def get_emote_count_by_ids(self, ids):
        cur = db.cursor()
        _idstr = " ,".join(["{}"]*len(ids)).format(*ids)
        try:
            cur.execute(f"SELECT * FROM emotes WHERE discord_id IN ({_idstr}) ORDER BY count DESC")
            return cur.fetchall()
        except:
            return None

    def increment_emote(self, id, name):
        cur = db.cursor()
        if not id:
            return
        try:
            cur.execute("SELECT * FROM emotes WHERE discord_id=? AND name=?", (id, name))
            cur.fetchone()[0]
        except:
            cur.execute("INSERT INTO emotes (discord_id,name,count) VALUES (?,?,?)", (id, name, 1))
        else:
            cur.execute("UPDATE emotes SET count=count+1 WHERE discord_id=? AND name=?", (id,name))
        finally:
            db.commit()

    def decrement_emote(self, id, name):
        cur = db.cursor()
        if not id:
            return
        try:
            cur.execute("SELECT * FROM emotes WHERE discord_id=? AND name=?", (id, name))
            cur.fetchone()[0]
        except:
            cur.execute("INSERT INTO emotes (discord_id,name,count) VALUES (?,?,?)", (id, name, 1))
        else:
            cur.execute("UPDATE emotes SET count=count-1 WHERE discord_id=? AND name=?", (id, name))
        finally:
            db.commit()

    def clear_emotes(self):
        cur = db.cursor()
        try:
            cur.execute("UPDATE emotes SET count=0")
        except:
            print("Error Clearing Emotes")
        finally:
            db.commit()

    @commands.Cog.listener("on_message")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def count_message_emotes(self, message):
        if message.author.bot:
            return

        if message.content.startswith(config["BOT"]["PREFIX"]):
            return

        if message.guild.id != self.guild:
            return

        custom_emojis = re.findall(r'<:\w*:\d*>', message.content)
        _counted = []
        for s in custom_emojis:
            s = s.replace("<", "").replace(">", "")
            _emoji = s.split(":")
            _emoji_id = int(_emoji[2])
            if _emoji_id not in _counted:
                _counted.append(_emoji_id)
                _emoji_obj = discord.utils.get(message.guild.emojis, id=_emoji_id)
                if _emoji_obj is not None:
                    self.increment_emote(_emoji_obj.id, _emoji_obj.name)

    @commands.Cog.listener("on_raw_reaction_add")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _on_react_count_emote(self, payload):
        _member = payload.member
        _reaction = payload.emoji
        _guild = self.bot.get_guild(payload.guild_id)
        _user = _guild.get_member(_member)

        if _member.bot:
            return

        if payload.guild_id != self.guild:
            return

        self.increment_emote(_reaction.id, _reaction.name)

    @commands.Cog.listener("on_raw_reaction_remove")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def _on_unreact_count_emote(self, payload):
        _member = payload.member
        _reaction = payload.emoji
        if _member and _member.bot:
            return

        if payload.guild_id != self.guild:
            return

        self.decrement_emote(_reaction.id, _reaction.name)

    @commands.command(name='emoteusage')
    async def _emote_usage(self, ctx, *, args=""):
        if ctx.author.bot:
            return
        # figure out how many results we're returning
        _results = None
        if args != "":
            custom_emojis = re.findall(r'<:\w*:\d*>', args)
            _counted = []
            for s in custom_emojis:
                s = s.replace("<", "").replace(">", "")
                _emoji = s.split(":")
                _emoji_id = int(_emoji[2])
                if _emoji_id not in _counted:
                    _counted.append(_emoji_id)
            _results = self.get_emote_count_by_ids(_counted)
        else:
            _results = self.get_emote_count_all()

        # return our results
        _i = 0
        _msg = ""
        for _row in _results:
            _emoji_id = int(_row[1])
            _emoji_use = int(_row[3])
            _emoji_obj = discord.utils.get(ctx.guild.emojis, id=_emoji_id)
            if _emoji_obj and _emoji_use > 0:
                _msg += f"{_emoji_obj} has been used {_emoji_use} time(s)\n"
                _i += 1
                if _i == 15:
                    _embed = Embed(description=_msg)
                    await ctx.channel.send(embed=_embed)
                    _i = 0
                    _msg = ""
                    _is_owner = await self.bot.is_owner(ctx.author)
                    if not (_is_owner or ctx.channel.id == config["BOT"]["BOT_CHANNEL"]):
                        await ctx.channel.send("Drink verification can [use the bot channel] to see full list.")
                        return

        if _msg:
            _embed = Embed(description=_msg)
            await ctx.channel.send(embed=_embed)

    @_emote_usage.error
    async def _emote_usage_error_handler(self, ctx, error):
        await ctx.channel.send("Hmm... looks like something went wrong. Check your formatting and try again.")

    @commands.command(name='clearemoteusage')
    @commands.is_owner()
    async def _clear_emote_usage(self, ctx):
        self.clear_emotes()
        await ctx.channel.send("Emote Usage Stats Cleared.")


async def setup(bot):
    await bot.add_cog(EmotesCog(bot))
