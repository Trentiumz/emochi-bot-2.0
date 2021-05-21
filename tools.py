import requests
import database
import re
import os
import discord

lines = {x.split(": ")[0]: x.split(": ")[1] for x in open("./info.txt", "rt").readlines()}

emote_path = "./data/emotes/"
emote_file_name_list = os.listdir(emote_path)
# emote_file_names[ending] = set of files with that ending
emote_file_names = {"png": set([x for x in emote_file_name_list if re.match(".*\.png", x)]),
                    "gif": set([x for x in emote_file_name_list if re.match(".*\.gif", x)])}


async def get_hook_url(channel: discord.TextChannel) -> str:
    return await database.get_webhook(channel)


# send webhook imitating another user
async def webhook_imitate(message: str, user: discord.User, channel: discord.TextChannel, file: discord.File = None):
    hook = discord.Webhook.from_url(await get_hook_url(channel), adapter=discord.RequestsWebhookAdapter())
    if file:
        embed = discord.Embed()
        embed.set_image(url="attachment://tmp.png")
    hook.send(content=message, wait=False, username=str(user.display_name), avatar_url=str(user.avatar_url), file=file,
              embed=embed)


# send an empty webhook
async def webhook_empty(message: str, channel: discord.TextChannel, file: discord.File = None):
    hook = discord.Webhook.from_url(await get_hook_url(channel), adapter=discord.RequestsWebhookAdapter())
    if file:
        embed = discord.Embed()
        embed.set_image(url="attachment://tmp.png")
    hook.send(content=message, wait=False, file=file, embed=embed)


# replace the current emote with a new one
async def replace_emote(to_remove: discord.Emoji, new_name: str, new_image: bytes) -> discord.Emoji:
    guild: discord.Guild = to_remove.guild
    await to_remove.delete()
    return await guild.create_custom_emoji(name=new_name, image=new_image)


# add an emote to the server
async def add_emote(name: str, image: bytes, guild: discord.Guild) -> discord.Emoji:
    return await guild.create_custom_emoji(name=name, image=image)


# get the image of some emote name
def image_at(emote_name: str) -> bytes:
    for ending in emote_file_names:
        if f"{emote_name}.{ending}" in emote_file_names[ending]:
            return open(f"{emote_path}{emote_name}.{ending}", "rb").read()
