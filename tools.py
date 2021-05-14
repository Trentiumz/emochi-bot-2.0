import requests
import re
from io import BytesIO
import discord

lines = {x.split(": ")[0]: x.split(": ")[1] for x in open("./info.txt", "rt").readlines()}

def get_hook_url():
    return lines["hook_url"]

def webhook_imitate(message: str, user: discord.User):
    hook_url = get_hook_url()
    obj = {
        "content": message,
        "username": str(user.display_name),
        "avatar_url": str(user.avatar_url)
    }

    requests.post(hook_url, json=obj)

def webhook_empty(message: str):
    hook_url = get_hook_url()
    obj = {
        "content": message
    }
    requests.post(hook_url, json=obj)


def regify(thing: str):
    return re.sub("\*", "\\*", thing)

async def replace_emote(to_remove: discord.Emoji, new_name: str, new_image: bytes):
    guild: discord.Guild = to_remove.guild
    await to_remove.delete()
    return await guild.create_custom_emoji(name=regify(new_name), image=new_image)

def image_at(url: str):
    return BytesIO(requests.get(str(url)).content).read()

# emotes: [(name, image)]
async def add_emotes(emotes: list, guild: discord.Guild, links: dict):
    limit = guild.emoji_limit
    # index we should start to replace instead of add emotes
    start_replace_ind = min(len(emotes), limit - len(guild.emojis))
    ids = {}

    # add all emotes possible
    existing_emotes = {str(x.name): x for x in guild.emojis}
    for i in range(start_replace_ind):
        if emotes[i] in existing_emotes:
            ids[emotes[i]] = existing_emotes[emotes[i]]
        else:
            ids[emotes[i]] = await guild.create_custom_emoji(name=regify(emotes[i]), image=image_at(links[emotes[i]]))

    # replace all of the remaining emotes
    for i in range(start_replace_ind, len(emotes)):
        ids[emotes[i]] = await replace_emote(guild.emojis[i - start_replace_ind], emotes[i], image_at(links[emotes[i]]))

    # ids: {name: emote object}
    return ids