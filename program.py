import discord
import database
import emote_detection

async def on_ready(client: discord.Client):
    print(f"{client.user} connected")
    database.init()

async def on_message(message: discord.Message):
    if not message.author.bot:

        # send a webhook
        await emote_detection.send_webhook(message)
