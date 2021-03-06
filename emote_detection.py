from sync_queue import SyncQueue
import asyncio
import tools
import discord
import re
import database

# emotes: list of emote names
async def add_emotes(emote_names: set, guild: discord.Guild) -> dict:
    limit = guild.emoji_limit
    guild_emotes = guild.emojis
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
        emotes[i] = await guild.create_custom_emoji(name=i, image=tools.image_at(i))
        curDB.append(i)

    # replace all of the remaining emotes
    for i in range(len(replace)):
        emotes[replace[i]] = await tools.replace_emote(existing_emotes[curDB.popleft()], replace[i], tools.image_at(replace[i]))
        curDB.append(replace[i])

    # emotes: {name: emote object}
    database.save_priorities()
    return emotes


# find what emote names we need
def needed_emotes(message: str) -> list:
    # remove emotes that are already processed
    message = re.sub("<:.+:\d+>|<a:.+:\d+>", "", message)
    # find all remaining wanted emotes (that we have)
    needed = {x[1:-1] for x in re.findall(tools.regex_for_emotes, message)}
    return list(needed)

def make_emotes_important(message: str, guild: discord.Guild):
    emotes = re.findall("<:.+:\d+>|<a:.+:\d+>", message)
    curDB: SyncQueue = database.get_priorities(guild.id)
    if len(emotes) == 0:
        return
    for i in emotes:
        name = i.split(":")[1]
        curDB.move_to_front(name)
    database.save_priorities()

webhook_updating = False


# if the new message has emotes, then resend the message
async def send_webhook(message: discord.Message):
    # wait until the webhook stops updating
    global webhook_updating
    while webhook_updating:
        await asyncio.sleep(0.07)

    webhook_updating = True
    guild: discord.Guild = message.guild

    # emotes that are used will be moved to the front of the queue
    make_emotes_important(message.content, message.guild)

    # get the emotes to replace, all just pure names of the emotes
    needed = list(needed_emotes(message.content))
    # if there aren't any replacements needed, then don't do anything
    if len(needed) == 0:
        webhook_updating = False
        return

    # if he needs too many emotes, then boop we quit it
    if len(needed) > guild.emoji_limit // 5:
        await tools.webhook_empty(f"Turns out the server doesn't have enough emote slots to hold your {len(needed)} emotes!", message.channel)
        webhook_updating = False
        return

    # update emotes in the server
    loaded_emotes = await add_emotes(set(needed), guild)

    # update the message to replace it all with updated emotes
    k = message.content
    for emote_name in loaded_emotes:
        k = re.sub(f":{emote_name}:", str(loaded_emotes[emote_name]), k)

    # send the new message & delete original
    file = None
    if len(message.attachments) > 0:
        await message.attachments[0].save(fp="./data/tmp.png")
        file = discord.File(fp="./data/tmp.png")
    await tools.webhook_imitate(k, message.author, message.channel, file=file)

    webhook_updating = False
    await message.delete()
