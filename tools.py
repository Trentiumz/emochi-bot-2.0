import requests
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