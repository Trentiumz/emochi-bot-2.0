from sync_queue import SyncQueue
import asyncio
from tools import *
import re
import database

# list of emotes but formatted for regex
emotes = [f":{s.split('.')[0]}:" for s in emote_file_name_list]
# a regex for which we can find all of the possible emotes
regex_for_emotes = "|".join(emotes)

# emotes: list of emote names
async def add_emotes(emote_names: set, guild: discord.Guild) -> dict:
    limit = guild.emoji_limit
    guild_emotes = await guild.fetch_emojis()
    curDB: SyncQueue = database.get_priorities(guild.id)
    curDB.sync({x.name for x in guild_emotes})

    # index we should start to replace instead of add emotes
    num_to_add = (limit - len(guild_emotes))
    emotes = {}
    existing_emotes = {str(x.name): x for x in guild_emotes}

    # make sure to replace existing emotes
    for i in emote_names:
        if i in existing_emotes:
            emotes[i] = existing_emotes[i]
    for i in emotes:
        emote_names.remove(i)
        curDB.move_to_front(i)

    # get what else we still need to add
    emote_names = list(emote_names)
    add_to = emote_names[:num_to_add]
    replace = emote_names[num_to_add:]

    # add all emotes possible
    for i in add_to:
        emotes[i] = await guild.create_custom_emoji(name=i, image=image_at(i))
        curDB.append(i)

    # replace all of the remaining emotes
    for i in range(len(replace)):
        emotes[replace[i]] = await replace_emote(existing_emotes[curDB.popleft()], replace[i], image_at(replace[i]))
        curDB.append(replace[i])

    # emotes: {name: emote object}
    database.save_priorities()
    return emotes


# find what emote names we need
def needed_emotes(message: str) -> list:
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
        webhook_updating = False
        return
    # if he needs too many emotes, then boop we quit it
    if len(needed) > guild.emoji_limit // 5:
        await webhook_empty(f"Turns out the server doesn't have enough emote slots to hold your {len(needed)} emotes!", message.channel)
        webhook_updating = False
        return

    # update emotes in the server
    loaded_emotes = await add_emotes(set(needed), guild)

    # update the message to replace it all with updated emotes
    k = message.content
    for emote_name in loaded_emotes:
        k = re.sub(f":{emote_name}:", str(loaded_emotes[emote_name]), k)

    # send the new message & delete original
    await webhook_imitate(k, message.author, message.channel)

    webhook_updating = False
    await message.delete()
