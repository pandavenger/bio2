from config import config, db
import random

import discord
from discord.ext import commands

import asyncio


class RepliesCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.vaginas = 0
        self.get_vaganias()

    def get_vaganias(self):
        cur = db.cursor()
        try:
            cur.execute("SELECT * FROM options WHERE name=?", ["vaginas"])
            self.vaginas = int(cur.fetchone()[2])
        except:
            cur.execute('INSERT INTO options (name,value) VALUES (?, 422);', ["vaginas"])
            self.vaginas = 1
            db.commit()

    def set_vaganias(self, n):
        self.vaginas = n
        cur = db.cursor()
        try:
            cur.execute("UPDATE options SET value=? WHERE name=?", (n, "vaginas"))
        except:
            cur.execute('INSERT INTO options (name,value) VALUES(?,?)', ("vaginas", n))
        db.commit()

    @commands.Cog.listener("on_message")
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=True)
    async def fun_replies(self, message):
        msg_text = message.clean_content.lower()
        msg_text_word_only = msg_text.split()

        # cannot reply to itself
        if message.author == self.bot.user:
            return

        # imagine
        if msg_text.replace(" ", "") == "imagine":
            self.set_vaganias((self.vaginas + 1))
            await message.channel.send(str(self.vaginas) + " VAGINAS")

        # rrreee
        if '883' in msg_text_word_only:
            _streeng = ('r' * random.randint(1, 10)) + ('e' * random.randint(2, 16))
            # print(message.content)
            await message.channel.send(_streeng)

        if any(word in msg_text for word in
               ["thanks bio2", "thanks biochem2", "thank you bio2", "thank you biochem2"]):
            await message.channel.send("you're welcome")

        # if "kimi no sei" in msg_text:
        #    if random.randint(0, 3) > 1:
        #        await message.channel.send("KIMI NO SEI")

        if "jazz" in msg_text:
            if random.randint(0, 10) == 10:
                await message.channel.send("JAZZ BAD")

        if msg_text == 'my wife':
            if random.randint(0, 2) == 4:
                await asyncio.sleep(30)
                await message.delete()
                if random.randint(0, 500000) == 1000000:
                    await message.channel.send("NO MY WIFE")

        # if "enema" in msg_text_word_only:
        #    if random.randint(0, 3) > 1:
        #        await message.channel.send("I happen to be an expert on this subject")

        # if "ass" in msg_text_word_only:
        #    if random.randint(0, 20) == 20:
        #        await message.channel.send("Well, MY ASS is famous!")

        if any(word in msg_text for word in ["among us", "amogus", "amoongus"]) or "sus" in msg_text_word_only:
            if random.randint(0, 10) == 10:
                await message.channel.send("sus")

        if any(word in msg_text for word in ["makima", "woof"]):
            if random.randint(0, 4) == 4:
                _barkstr = ""
                _numwoofs = random.randint(8,24)
                for x in range(_numwoofs):
                    _barkstr += random.choice(["WOOF", "WOOF", "WOOF", "BARK", "BARK", "GROWL", "SNARL", "AWOOOO", "ARF"])
                    if x != (_numwoofs-1):
                        _barkstr += " "
                await message.channel.send(_barkstr)

        if "egg" in msg_text_word_only:
            if random.randint(0, 10) == 1:
                await message.channel.send("egg time")

        if "wilson" in msg_text_word_only:
            if random.randint(0, 1000) == 1:
                await message.channel.send("I'm going to BOMB wilson's house!")

        if "tiger" in msg_text_word_only:
            if random.randint(0, 1000) == 1:
                await message.channel.send("I'm going to give Tiger's feet a kissy-wissy")


async def setup(bot):
    await bot.add_cog(RepliesCog(bot))
