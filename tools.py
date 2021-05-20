import requests
import re
import os
import discord

lines = {x.split(": ")[0]: x.split(": ")[1] for x in open("./info.txt", "rt").readlines()}

emote_path = "./data/emotes/"
emote_file_name_list = os.listdir(emote_path)
# emote_file_names[ending] = set of files with that ending
emote_file_names = {"png": set([x for x in emote_file_name_list if re.match(".*\.png", x)]),
                    "gif": set([x for x in emote_file_name_list if re.match(".*\.gif", x)])}


def get_hook_url() -> str:
    return lines["hook_url"]


# send webhook imitating another user
def webhook_imitate(message: str, user: discord.User):
    hook_url = get_hook_url()
    obj = {
        "content": message,
        "username": str(user.display_name),
        "avatar_url": str(user.avatar_url)
    }

    requests.post(hook_url, json=obj)


# send an empty webhook
def webhook_empty(message: str):
    hook_url = get_hook_url()
    obj = {
        "content": message
    }
    requests.post(hook_url, json=obj)


# replace the current emote with a new one
async def replace_emote(to_remove: discord.Emoji, new_name: str, new_image: bytes) -> discord.Emoji:
    guild: discord.Guild = to_remove.guild
    await to_remove.delete()
    return await guild.create_custom_emoji(name=new_name, image=new_image)


async def add_emote(name: str, image: bytes, guild: discord.Guild) -> discord.Emoji:
    return await guild.create_custom_emoji(name=name, image=image)


def image_at(emote_name: str) -> bytes:
    for ending in emote_file_names:
        if f"{emote_name}.{ending}" in emote_file_names[ending]:
            return open(f"{emote_path}{emote_name}.{ending}", "rb").read()
