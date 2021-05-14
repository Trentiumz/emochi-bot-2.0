import discord
import asyncio
import re
import tools

# links: {name: link}
links = {x.split("|")[0]: x.split("|")[1].rstrip()for x in open("./emoji_links.txt", "rt").readlines()}

# list of emotes but formatted for regex
emotes = []
for key in links:
    s = re.sub("\*", "\\*", key)
    emotes.append(f":{s}:")

# a regex for which we can find all of the possible emotes
regex_for_emotes = "|".join(emotes)
print(regex_for_emotes)


async def on_ready(client: discord.Client):
    print(f"{client.user} connected")

# find what emote names we need
def needed_emotes(message: str, guild: discord.Guild):
    message = re.sub("|".join(str(emote) for emote in guild.emojis), "", message)
    needed = [x[1:-1] for x in re.findall(regex_for_emotes, message)]
    return list(set(needed))

# replace the areas with their corresponding emote id
# needed_emotes: {name: Emoji Object}
def replace_with_emotes(message: str, loaded_emotes: dict):
    for emote_name in loaded_emotes:
        message = re.sub(f":{tools.regify(emote_name)}:", str(loaded_emotes[emote_name]), message)
    return message

webhook_updating = False
async def send_webhook(needed: list, cur_guild: discord.Guild, message: discord.Message):
    global webhook_updating
    while webhook_updating:
        await asyncio.sleep(0.01)

    webhook_updating = True
    await asyncio.sleep(1)
    # update emotes and get the update message
    needed_ids = await tools.add_emotes(needed, cur_guild, links)
    k = replace_with_emotes(message.content, needed_ids)

    # send the new message
    tools.webhook_imitate(k, message.author)
    webhook_updating = False

async def on_message(message: discord.Message):
    if not message.author.bot:

        # get the current guild
        cur_guild: discord.Guild = message.guild

        # get the emotes to replace, all just pure names of the emotes
        needed = list(needed_emotes(message.content, cur_guild))

        if len(needed) > cur_guild.emoji_limit:
            tools.webhook_empty(
                f"Turns out the server doesn't have enough emote slots to hold your {len(needed)} emotes!")
            return

        # send a webhook
        await send_webhook(needed, cur_guild, message)

        # delete the original message
        await message.delete()
