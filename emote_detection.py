import discord
import asyncio
import tools
import re

# links: {name: link}
links = {x.split("|")[0]: x.split("|")[1].rstrip() for x in open("./emoji_links.txt", "rt").readlines()}

# list of emotes but formatted for regex
emotes = [f":{s}:" for s in links]

# a regex for which we can find all of the possible emotes
regex_for_emotes = "|".join(emotes)


# find what emote names we need
def needed_emotes(message: str):
    # remove emotest that are already processed
    message = re.sub("<:.+:\d+>|<a:.+:\d+>", "", message)
    # find all remaining wanted emotes (that we have)
    needed = {x[1:-1] for x in re.findall(regex_for_emotes, message)}
    return list(needed)


webhook_updating = False


# if the new message has emotes, then resend the message
async def send_webhook(message: discord.Message):
    # wait until the webhook stops updating
    global webhook_updating
    while webhook_updating:
        await asyncio.sleep(0.07)

    webhook_updating = True
    guild: discord.Guild = message.guild


    # get the emotes to replace, all just pure names of the emotes
    needed = list(needed_emotes(message.content))
    if len(needed) == 0:
        return
    # if he needs too many emotes, then boop we quit it
    if len(needed) > guild.emoji_limit // 3:
        tools.webhook_empty(
            f"Turns out the server doesn't have enough emote slots to hold your {len(needed)} emotes!")
        return


    # update emotes in the server
    loaded_emotes = await tools.add_emotes(needed, guild, links)


    # update the message to replace it all with updated emotes
    k = message.content
    for emote_name in loaded_emotes:
        k = re.sub(f":{emote_name}:", str(loaded_emotes[emote_name]), k)


    # send the new message & delete original
    tools.webhook_imitate(k, message.author)
    webhook_updating = False
    await message.delete()
