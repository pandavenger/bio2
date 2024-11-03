from config import config, db
import re
import traceback
import sys

import discord
from discord import Embed, Emoji
from discord.ext import commands


class PingsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild = config["BOT"]["PRIMARY_GUILD"]

    def get_all_active_groups(self):
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM groups WHERE active=1")
            return cur.fetchall()
        except:
            return None

    def get_group_by_name(self, name):
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM groups WHERE active=1 AND name=?", [name])
            return cur.fetchone()
        except:
            return None

    def get_group_by_id(self, id):
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM groups WHERE active=1 AND id=?", [id])
            return cur.fetchone()
        except:
            return None

    def delete_group_by_id(self, id):
        cur = db.cursor()
        name = ""
        try:
            cur.execute("DELETE FROM group_members WHERE group_id=?", [id])
            cur.execute("SELECT * FROM groups WHERE active=1 AND id=?", [id])
            name = cur.fetchone()[1]
        except:
            return name
        else:
            cur.execute("UPDATE groups SET active=0 WHERE id=?", [id])
            db.commit()
            return name

    def create_group(self, name):
        cur = db.cursor()
        _id = 0
        try:
            cur.execute("SELECT * FROM groups WHERE name=?", [name])
            cur.fetchone()[0]
        except:
            cur.execute("INSERT INTO groups (name) VALUES (?)", [name])
            _id = cur.lastrowid
        else:
            cur.execute("UPDATE groups SET active=1 WHERE name=?", [name])
            _id = cur.lastrowid
        finally:
            db.commit()
            return _id

    def add_user_to_group(self, group_id, user_id, name):
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO group_members (group_id, discord_id, name) VALUES (?,?,?)", (group_id, user_id, name))
        except:
            return
        db.commit()

    def delete_user_from_group(self, group_id, user_id, name):
        cur = db.cursor()
        print(user_id)
        try:
            cur.execute("DELETE FROM group_members WHERE group_id=? AND discord_id=?", (group_id, user_id))
        except:
            return
        db.commit()

    def get_all_users_in_group(self, group_id):
        cur = db.cursor()
        try:
            cur.execute("""
                SELECT group_members.discord_id, group_members.name
                FROM group_members
                LEFT JOIN groups
                ON group_members.group_id=groups.id
                WHERE groups.id=? AND groups.active=1
                """, (group_id,))
            return cur.fetchall()
        except:
            return None


    @commands.command(name='group-create', aliases=['gc'],
                      brief="Create a Group",
                      help="Create a Group. Use \"Name Goes Here\" for names with spaces.")
    async def _group_create(self, ctx, arg):
        if arg == "":
            return

        if ctx.author.bot:
            return

        group = self.get_group_by_name(arg)
        if group is not None:
            await ctx.message.channel.send("There already exists an active group with that name.")
            return

        if len(ctx.message.mentions) > 0:
            await ctx.message.channel.send("Please do not include pings in the group name, that's just rude.")
            return

        group = self.create_group(arg)
        if group > 0:
            await ctx.message.channel.send(f"Group #{group} created with the name {arg}")

    @commands.command(name='group-status', aliases=['gs'],
                      brief="Get Group status",
                      help="Get Group status. Does not ping Group Members."
                           + "Use \"Name Goes Here\" for names with spaces.")
    async def _group_status(self, ctx, arg):
        if arg == "":
            return

        if ctx.author.bot:
            return

        regex = '^[0-9]+$'
        if re.search(regex, arg):
            group = self.get_group_by_id(int(arg))
        else:
            group = self.get_group_by_name(arg)

        if group is not None:
            _msg = f"Group #{group[0]} ({group[1]}) exists with the members:"
            members = self.get_all_users_in_group(int(group[0]))
            _i = 0
            if members:
                for member in members:
                    _mention = f" {member[1]}"
                    _msg += _mention
                    _i += 1
                    if _i > 20:
                        await ctx.message.channel.send(_msg)
                        _msg = ""
                        _i = 0
            if _msg:
                await ctx.message.channel.send(_msg)
        else:
            await ctx.message.channel.send("Group not found using the query " + arg)

    @commands.command(name='group-delete', aliases=['gd'],
                      brief="Delete a Group",
                      help="Delete a Group. Use \"Name Goes Here\" for names with spaces.")
    async def _group_delete(self, ctx, arg):
        if arg == "":
            return

        if ctx.author.bot:
            return

        regex = '^[0-9]+$'
        if re.search(regex, arg):
            group = self.get_group_by_id(int(arg))
        else:
            group = self.get_group_by_name(arg)

        if group is not None:
            self.delete_group_by_id(int(group[0]))
            await ctx.message.channel.send(f"Group #{group[0]} ({group[1]}) was deleted")
        else:
            await ctx.message.channel.send("Group not found using the query " + arg)

    @commands.command(name='group-add', aliases=['ga'],
                      brief="Add Group Member(s)",
                      help="Add Group Member(s). The first argument is the Group ID or Name,"
                           + "and the rest is parsed for possible Group Members.")
    async def _group_add(self, ctx, arg, members: commands.Greedy[discord.Member]):
        if arg == "":
            return

        if ctx.author.bot:
            return

        regex = '^[0-9]+$'
        if re.search(regex, arg):
            group = self.get_group_by_id(int(arg))
        else:
            group = self.get_group_by_name(arg)

        if group is not None:
            for member in members:
                self.add_user_to_group(int(group[0]), int(member.id), member.name)
                await ctx.message.channel.send(member.name + f" added to Group #{group[0]} ({group[1]})")
        else:
            await ctx.message.channel.send("Group not found using the query " + arg)

    @commands.command(name='group-remove', aliases=['gr'],
                      brief="Remove Group Member(s)",
                      help="Remove Group Member(s). The first argument is the Group ID or Name,"
                           + "and the rest is parsed for possible Group Members.")
    async def _group_remove(self, ctx, arg, members: commands.Greedy[discord.Member]):
        if arg == "":
            return

        if ctx.author.bot:
            return

        regex = '^[0-9]+$'
        if re.search(regex, arg):
            group = self.get_group_by_id(int(arg))
        else:
            group = self.get_group_by_name(arg)

        if group is not None:
            for member in members:
                self.delete_user_from_group(int(group[0]), member.id, member.name)
                await ctx.message.channel.send(member.name + f" removed from to Group #{group[0]} ({group[1]})")
        else:
            await ctx.message.channel.send("Group not found using the query " + arg)

    @commands.command(name='group-ping', aliases=['gp'],
                      brief="Ping Group Member(s)",
                      help="Ping Group Member(s). Please use responsibly")
    async def _group_ping(self, ctx, arg):
        if arg == "":
            return

        if ctx.author.bot:
            return

        regex = '^[0-9]+$'
        if re.search(regex, arg):
            group = self.get_group_by_id(int(arg))
        else:
            group = self.get_group_by_name(arg)

        if group is not None:
            _msg = f"Group #{group[0]} ({group[1]}) "
            members = self.get_all_users_in_group(int(group[0]))
            _i = 0
            if members:
                for member in members:
                    _mention = f"<@{member[0]}>"
                    _msg += _mention
                    _i += 1
                    if _i > 20:
                        await ctx.message.channel.send(_msg)
                        _msg = ""
                        _i = 0
            if _msg:
                await ctx.message.channel.send(_msg)

        else:
            await ctx.message.channel.send("Group not found using the query " + arg)

    @commands.command(name='group-list', aliases=['gl'],
                      brief="List active groups",
                      help="List active groups by Name and ID.")
    async def _group_list(self, ctx):
        if ctx.author.bot:
            return

        groups = self.get_all_active_groups()

        _i = 0
        _msg = ""
        for _row in groups:
            _msg += f"Group #{_row[0]} ({_row[1]})\n"
            _i += 1
            if _i == 20:
                _embed = Embed(description=_msg)
                await ctx.channel.send(embed=_embed)
                _i = 0
                _msg = ""
        if _msg:
            _embed = Embed(description=_msg)
            await ctx.channel.send(embed=_embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound,)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                await ctx.send('I could not find that member. Please try again.')

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


async def setup(bot):
    await bot.add_cog(PingsCog(bot))
