from sync_queue import SyncQueue
import discord

emotes_path = "./data/guild_info.txt"
webhook_path = "./data/channel_webhooks.txt"

# guild id: guild_priority_list
priorities = {}

# channel id : webhook url
webhooks = {}

# initialize the database with the files on the guilds and webhooks
def init():
    try:
        # open the file for emotes
        with open(emotes_path, "rt") as file:
            lines = file.readlines()
            for i in lines:
                parts = i.split()
                guild_id = int(parts[0])

                priorities[guild_id] = SyncQueue()

                name_priorities = parts[1:]
                for i in name_priorities:
                    priorities[guild_id].append(i)

    except FileNotFoundError:
        open(emotes_path, "x")

    try:
        # open the file for the webhooks per channel
        with open(webhook_path, "rt") as file:
            lines = file.readlines()
            for i in lines:
                parts = i.split()
                webhooks[int(parts[0])] = parts[1]
    except FileNotFoundError:
        open(webhook_path, "x")

# get an object for the emote priorities of the current guild
def get_priorities(id_of: int) -> SyncQueue:
    if id_of not in priorities:
        priorities[id_of] = SyncQueue()
    return priorities[id_of]

# save the priorities to the list
def save_priorities():
    with open(emotes_path, "wt") as output:
        outputs = []
        for id_of in priorities:
            outputs.append(" ".join([str(id_of)] + list(priorities[id_of].main)))
        output.write("\n".join(outputs))

# get the webhook url for the current channel
async def get_webhook(channel: discord.TextChannel) -> str:
    if channel.id not in webhooks:
        await new_webhook(channel)
    return webhooks[channel.id]

# create a new webhook for the current channel
async def new_webhook(channel: discord.TextChannel):
    webhook: discord.Webhook = await channel.create_webhook(name="Emochi Bot 2 Webhook")
    webhooks[channel.id] = webhook.url
    save_webhooks()

# save the webhook urls to the file
def save_webhooks():
    with open(webhook_path, "wt") as output:
        outputs = []
        for channel_id in webhooks:
            outputs.append(f"{channel_id} {webhooks[channel_id]}")
        output.write("\n".join(outputs))