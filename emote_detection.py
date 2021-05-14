import discord
import asyncio
import tools
import re


# find what emote names we need
def needed_emotes(message: str, regex_for_emotes: str):
    message = re.sub("<:.+:\d+>|<a:.+:\d+>", "", message)
    needed = [x[1:-1] for x in re.findall(regex_for_emotes, message)]
    return list(set(needed))


webhook_updating = False
# sends a webhook with the new message, updating the needed emotes
async def send_webhook(needed: list, cur_guild: discord.Guild, message: discord.Message, links: dict):
    # wait until the webhook stops updating
    global webhook_updating
    while webhook_updating:
        await asyncio.sleep(0.01)

    webhook_updating = True
    await asyncio.sleep(1)

    # update emotes and get the update message
    loaded_emotes = await tools.add_emotes(needed, cur_guild, links)

    # update the message to replace it all with updated emotes
    k = message.content
    for emote_name in loaded_emotes:
        k = re.sub(f":{tools.regify(emote_name)}:", str(loaded_emotes[emote_name]), k)

    # send the new message
    tools.webhook_imitate(k, message.author)
    webhook_updating = False
