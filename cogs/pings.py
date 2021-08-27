from config import config, db
import re

import discord
from discord import Embed, Emoji
from discord.ext import commands


class EmotesCog(commands.Cog):

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


    @commands.command(name='group-create', aliases=['gc'])
    async def _group_create(self, ctx, arg):
        if arg == "":
            return

        if ctx.author.bot:
            return

        if len(ctx.message.mentions) > 0:
            await ctx.message.channel.send("Please do not include pings in the group name, that's just rude.")
            return

        group = self.create_group(arg)
        if group > 0:
            await ctx.message.channel.send(f"Group #{group} created with the name {arg}")

    @commands.command(name='group-status', aliases=['gs'])
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

    @commands.command(name='group-delete', aliases=['gd'])
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

    @commands.command(name='group-add', aliases=['ga'])
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

    @commands.command(name='group-remove', aliases=['gr'])
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

    @commands.command(name='group-ping', aliases=['gp'])
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

    @commands.command(name='group-list', aliases=['gl'])
    async def _group_ping(self, ctx):
        if ctx.author.bot:
            return

        groups = self.get_all_active_groups()

        _i = 0
        _msg = ""
        for _row in groups:
            _msg += f"Group #{group[0]} ({group[1]})\n"
            _i += 1
            if _i == 20:
                _embed = Embed(description=_msg)
                await ctx.channel.send(embed=_embed)
                _i = 0
                _msg = ""
        if _msg:
            _embed = Embed(description=_msg)
            await ctx.channel.send(embed=_embed)

        else:
            await ctx.message.channel.send("Group not found using the query " + arg)

def setup(bot):
    bot.add_cog(EmotesCog(bot))
