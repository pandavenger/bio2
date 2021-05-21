# import random, asyncio is required for discord.py
import random
import asyncio
import json
from pysaucenao import AnimeSource, MangaSource, BooruSource, SauceNao

from bioaction import BioAction

# imports the required pieces from discord.py
import discord

# imports config file
import config

# import colors
from termcolor import cprint

import requests

# preload responses
# preload_responses_gpt2 = gpt2.generate(sess, run_name='biochem300', length=200, return_as_list=True)[0].splitlines()
# preload_responses = queue.Queue()
# for i, x in enumerate(preload_responses_gpt2):
#    if i + 1 != len(preload_responses_gpt2):
#        preload_responses.put(x)

client = discord.Client()
saucenao = SauceNao(
    api_key=config.sn_key,
    min_similarity=40.0,
    priority=[21, 22, 5]
)

actionqueue = []
channelpositions = {}
performing_action = False


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# @client.event
# async def on_guild_channel_update(before, after):
#     global channelpositions
#
#     gid = after.guild.id
#     cid = after.id
#
#     if gid in channelpositions and cid in channelpositions[gid] and channelpositions[gid][cid]["position"] is not after.position:
#         try:
#             await after.edit(position=channelpositions[gid][cid]["position"], category=before.category)
#         except Exception as e:
#             print(e)


@client.event
async def on_message(message):
    global actionqueue

    queuelength = len(actionqueue)

    msg_text = message.clean_content.lower()

    # cannot reply to itself
    if message.author == client.user:
        return

    # imagine
    if msg_text.replace(" ", "") == "imagine":
        actionqueue.append(BioAction(str(config.vaginaCounter) + " VAGINAS", message.channel))

        if config.vaginaCounter == 69:
            actionqueue.append(BioAction("nice", message.channel))

        config.vaginaCounter += 1
        config.data['vagina'] = config.vaginaCounter
        with open('data.json', 'w') as outfile:
            json.dump(config.data, outfile)

    # rrreee
    if '883' in msg_text.split():
        streeng = ('r' * random.randint(1, 8)) + ('e' * random.randint(2, 12))
        # print(message.content)
        actionqueue.append(BioAction(streeng, message.channel))

    if "top 10 reason" in msg_text or "top bio2 reason" in msg_text:
        actionqueue.append(BioAction(msg_text, message.channel, BioAction.Type.Generate, BioAction.GenType.TopTen))

    if "subvert" in msg_text and "expect" in msg_text:
        actionqueue.append(
            BioAction("I can't believe that ", message.channel, BioAction.Type.Generate, BioAction.GenType.Subvert))

    if any(word in msg_text for word in
           ["thanks bio2", "thanks biochem2", "thank you bio2", "thank you biochem2"]):
        actionqueue.append(BioAction("you're welcome", message.channel))

    if "kimi no sei" in msg_text:
        if random.randint(0, 3) > 2:
            actionqueue.append(BioAction("KIMI NO SEI", message.channel))

    if "jazz" in msg_text:
        if random.randint(0, 10) > 9:
            actionqueue.append(BioAction("JAZZ BAD", message.channel))

    if "enema" in msg_text.split():
        if random.randint(0, 3) > 2:
            actionqueue.append(BioAction("I happen to be an expert on this subject", message.channel))

    if "ass" in msg_text.split():
        if random.randint(0, 20) > 19:
            actionqueue.append(BioAction("Well, MY ASS is famous", message.channel))

    if client.user in message.mentions:
        if "cum" in msg_text:
            if random.randint(0, 1) > 0:
                actionqueue.append(BioAction("jeb!.", message.channel))
            else:
                actionqueue.append(BioAction("cum!.", message.channel))
        else:
            msg_text = msg_text.replace('bio2', '')
            actionqueue.append(
                BioAction(msg_text + "\n", message.channel, BioAction.Type.Generate, BioAction.GenType.Response))

    # if random.randint(0, 50) <= 1:
    #    actionqueue.append(
    #        BioAction(msg_text + "\n", message.channel, BioAction.Type.Generate, BioAction.GenType.Response))

    # if random.randint(0, 1000) > 999:
    #     try:
    #         emoji = discord.utils.get(client.emojis, name="sniped")
    #         await message.add_reaction(emoji)
    #     except Exception as e:
    #         print(e)

    # if random.randint(0, 10) > 9:
    #     _cleanstr = "%s%s" % (message.clean_content[0].upper(), message.clean_content[1:])
    #     actionqueue.append(BioAction(_cleanstr, message.channel, BioAction.Type.Grammar))

    # if random.randint(0, 20000) <= 1:
    #     try:
    #         await message.add_reaction(config.REACT_M)
    #         await message.add_reaction(config.REACT_I)
    #         await message.add_reaction(config.REACT_L)
    #         await message.add_reaction(config.REACT_D)
    #         await message.add_reaction(config.REACT_C)
    #         await message.add_reaction(config.REACT_A)
    #         await message.add_reaction(config.REACT_R)
    #         await message.add_reaction(config.REACT_P)
    #         await message.add_reaction(config.REACT_E)
    #         await message.add_reaction(config.REACT_T)
    #     except Exception as e:
    #         print(e)

    # if message.author.id == 432362332824403979:
    #     await message.channel.send("X said: " + message.content)
    #     for x in message.attachments:
    #         await message.channel.send("X attached:" + str(x.url))
    #     await message.delete()

    if queuelength == 0 and len(actionqueue) > 0 and not performing_action:
        await do_action()


@client.event
async def on_reaction_add(reaction, user):
    global actionqueue, saucenao

    queuelength = len(actionqueue)

    _message = reaction.message
    if reaction.emoji != config.REACT_SAUCE:
        return

    results = []
    original = []
    if len(_message.attachments) > 0:
        for attachment in _message.attachments:
            try:
                _result = await saucenao.from_url(attachment.url)
                if _result.short_remaining <= 0:
                    await asyncio.sleep(30)
            except Exception as e:
                _result = False

            results.append(_result)
            original.append(attachment.url)

    if len(_message.embeds) > 0:
        for embed in _message.embeds:
            try:
                _result = await saucenao.from_url(embed.url)
                if _result.short_remaining <= 0:
                    await asyncio.sleep(30)
            except Exception as e:
                _result = False
            results.append(_result)
            original.append(embed.url)

    i = 0
    for r in results:

        _thumbnail = original[i]
        _description = ""
        _url = ""
        _similarity = ""
        _title = ""
        _author = ""
        _chapter = -883
        _episode = -1
        _timestamp = ''

        if not r:
            _description = "What do I look like to you, a robot? Look it up yourself."
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
            _url = '[' + _url + '](' + _url + ')'
            _embed.add_field(name="Source", value=str(_url))

        actionqueue.append(BioAction(_embed, _message.channel, BioAction.Type.Embed))
        i += 1

    if queuelength == 0 and len(actionqueue) > 0 and not performing_action:
        await do_action()


async def do_action():
    global actionqueue, performing_action

    if len(actionqueue) <= 0:
        performing_action = False
        return

    performing_action = True

    action = actionqueue[0]
    if action._type == BioAction.Type.Message:
        await action._channel.send(action._msg)
        actionqueue.pop(0)

    elif action._type == BioAction.Type.Embed:
        await action._channel.send(embed=action._msg)
        actionqueue.pop(0)

    elif action._type == BioAction.Type.Generate:
        requesturl = "http://localhost:8080"
        params = {'msg': action._msg, 'type': action._gen.value}
        async with action._channel.typing():
            response = requests.get(requesturl, params)
        # print(response)
        try:
            await action._channel.send(response.text)
        except Exception as e:
            print(e)
            await action._channel.send("[ERROR] I seem to have shit in my own mouth. Try again later.")
        actionqueue.pop(0)

    elif action._type == BioAction.Type.Grammar:
        r = requests.post("https://grammarbot.p.rapidapi.com/check",
                          data={'text': action._msg, 'language': 'en-US'},
                          headers={
                              'x-rapidapi-host': "grammarbot.p.rapidapi.com",
                              'x-rapidapi-key': "your-key-here",
                              'content-type': "application/x-www-form-urlencoded"
                          })
        j = r.json()
        # print(j)
        new_text = ''
        sugg = ''
        cursor = 0
        corrected = False
        for match in j["matches"]:
            offset = match["offset"]
            length = match["length"]
            sugg = match["message"]

            if cursor > offset:
                continue
            error_text = action._msg[offset:(offset + length)]
            if match["rule"]["id"] == "MORFOLOGIK_RULE_EN_US":
                if len(error_text) < 4 or "Http" in error_text :
                    continue
            new_text += action._msg[cursor:offset]
            # next add **word**
            new_text += "**" + error_text + "**"
            corrected = True
            # update cursor
            cursor = offset + length
            break

            # if cursor < text length, then add remaining text to new_text
        if cursor < len(action._msg):
            new_text += action._msg[cursor:]

        # await action._channel.send("I found an error with your sentence:\n" + sugg)
        if corrected:
            try:
                await action._channel.send(sugg)
                await action._channel.send('> ' + new_text)
            except Exception as e:
                print(e)

        actionqueue.pop(0)

    if len(actionqueue) > 0:
        await do_action()
    else:
        performing_action = False


@client.event
async def on_ready():
    global channelpositions

    await client.change_presence(activity=discord.Game(name=random.choice(config.bio_gametext)))
    #
    cprint("Bot Online", 'green')
    cprint("name: {}".format(client.user.name), 'green')
    cprint("ID: {}".format(client.user.id), 'green')
    # await client.user.edit(avatar=config.pfpDefault)
    for server in client.guilds:
        cprint(server.name, 'yellow')
        channelpositions[server.id] = {}
        for channel in server.text_channels:
            channelpositions[server.id][channel.id] = {}
            channelpositions[server.id][channel.id]['position'] = channel.position
            channelpositions[server.id][channel.id]['category'] = channel.category
            cprint("{} p{} c{}".format(channel.name, channelpositions[server.id][channel.id]['position'], channelpositions[server.id][channel.id]['category']), 'yellow')


async def list_servers():
    global channelpositions

    await client.wait_until_ready()
    while not client.is_closed:
        await client.change_presence(game=discord.Game(name=random.choice(config.bio_gametext)))
        cprint("Current servers:", 'green')
        for server in client.guilds:
            cprint(server.name, 'yellow')
            channelpositions[server.id] = {}
            for channel in server.channels:
                channelpositions[server.id][channel.id] = channel.position
                cprint("{} {}".format(channel.name, channel.position), 'yellow')
        await asyncio.sleep(60)

client.run(config.TOKEN)
