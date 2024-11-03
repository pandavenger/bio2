from config import config, db

import discord
from discord.ext import tasks, commands

class ChannelsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_channels(self, server_id):
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM channels WHERE server_id=?", (server_id,))
            return cur.fetchall()
        except:
            return None

    async def set_channels(self, server_id, channels):
        cur = db.cursor()
        try:
            cur.execute("DELETE FROM channels WHERE server_id=?", (server_id, ))
        except Exception as e:
            print(e)
        else:
            try:
                for channel in channels:
                    _channel_id = channel.id
                    _channel_name = channel.name
                    _category_id = -1
                    _category_name = ""
                    _position = channel.position
                    if channel.category is not None:
                        _category_id = channel.category.id
                        _category_name = channel.category.name
                    cur.execute(
                        "INSERT INTO channels (server_id,channel_id,channel_name,category_id,category_name,position) VALUES (?,?,?,?,?,?)",
                        (server_id, _channel_id, _channel_name, _category_id, _category_name, _position))
            except Exception as e:
                print(e)
        finally:
            db.commit()

    @commands.command(name='setchannels')
    @commands.is_owner()
    async def _set_channel_order(self, ctx):
        _server = ctx.guild
        await self.set_channels(_server.id, _server.channels)
        await ctx.message.add_reaction(config["REACTS"]["CHECK"])

    @commands.command(name='cleanchannels')
    @commands.cooldown(1, 120.0, commands.BucketType.default)
    async def _clean_channel_order(self, ctx):
        _server = ctx.guild
        _channels = await self.get_channels(_server.id)
        for _channel in _channels:
            print(_channel)
            _server_channel = discord.utils.get(_server.channels, id=int(_channel[2]))
            if _server_channel:
                try:
                    await _server_channel.edit(position=_channel[6], category=discord.utils.get(_server.channels, id=_channel[4]))
                except Exception as e:
                    print(e)

        await ctx.message.add_reaction(config["REACTS"]["CHECK"])

    @commands.command(name='admincleanchannels')
    @commands.is_owner()
    async def _admin_clean_channel_order(self, ctx):
        _cc = self.bot.get_command('cleanchannels')
        await ctx.invoke(_cc)

    @_clean_channel_order.error
    async def _emote_usage_error_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(f"cool it bucko, try again in like... idk {error.retry_after} seconds")
        else:
            await ctx.channel.send("Hmm... looks like something went wrong. Check your formatting and try again.")


def setup(bot):
    bot.add_cog(ChannelsCog(bot))
