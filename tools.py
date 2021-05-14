import requests
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

async def replace_emote(to_remove: discord.Emoji, new_name: str, new_image: bytes):
    guild: discord.Guild = to_remove.guild
    await to_remove.delete()
    return await guild.create_custom_emoji(name=new_name, image=new_image)

async def add_emotes(emotes: list, guild: discord.Guild):
    limit = guild.emoji_limit
    # add all emotes possible
    for i in range(min(len(emotes), limit - len(guild.emojis))):
        await guild.create_custom_emoji(name=emotes[i][0], image=emotes[i][1])
    # replace all of the remaining emotes
    for i in range(min(len(emotes), limit - len(guild.emojis)), len(emotes)):
        await replace_emote(guild.emojis[i], emotes[i][0], emotes[i][1])

def image_at(url: str):
    return BytesIO(requests.get(str(url)).content).read()