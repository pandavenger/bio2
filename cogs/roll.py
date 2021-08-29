import re
import random

import discord
from discord.ext import tasks, commands


def roll(dice, sides, explode=-1):
    _dice = dice
    if dice <= 0:
        return
    _roll = random.randint(1, sides)
    if 0 < explode <= _roll:
        _dice += 1
    yield _roll
    yield from roll(_dice - 1, sides, explode)


class RollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roll',
                      brief="Roll a dice",
                      help="Roll a dice. Use params [n]d[sides]e[explode]s[success]. Rolls a 1d6e0s0 by default.\n" +
                           "All parameters are optional and e and s can be interchangeable (treated like flags).\n" +
                           "A 0 parameter for e and s will not count anything towards those parameters.\n\n" +
                           "Example: 1d10e10s8 for a normal World of Darkness die.")
    async def _roll(self, ctx, arg=""):
        arg = arg.lower()

        if "wod" in arg:
            _rdice = re.search(r"(\d+)(?=wod)", arg)

            _dice = 1 if not _rdice else int(_rdice.group(0))
            _sides = 10
            _exp = 10
            _succ = 8
        else:
            _rdice = re.search(r"(\d+)(?=d)", arg)
            _rsides = re.search(r"(?<=d)(\d+)(.*?)", arg)
            _rexp = re.search(r"(?<=e)(\d+)(.*?)", arg)
            _rsucc = re.search(r"(?<=s)(\d+)(.*?)", arg)

            _dice = 1 if not _rdice else int(_rdice.group(0))
            _sides = 6 if not _rsides else int(_rsides.group(0))
            _exp = 0 if not _rexp else int(_rexp.group(0))
            _succ = 0 if not _rsucc else int(_rsucc.group(0))

        _dicelist = list(roll(_dice, _sides, _exp))
        _sum = sum(_dicelist)
        _explodes = 0
        _explode_chains = 0
        _successes = 0
        _i = 1
        _out = ""
        for _roll in _dicelist:
            if _i == (_dice + 1):
                _out += "[ "
            if 0 < _succ <= _roll:
                _successes += 1
            if 0 < _exp <= _roll:
                _explodes += 1
                if _i > _dice:
                    _explode_chains += 1
            _out += str(_roll) + " "
            _i += 1

        if _explodes > 0:
            _out += "]"

        _out += "\n"
        _out += f"[{_successes} Successes][{_explodes} Explodes ({_explode_chains} Chained)][{_sum} Total]"

        await ctx.channel.send(_out)


def setup(bot):
    bot.add_cog(RollCog(bot))
