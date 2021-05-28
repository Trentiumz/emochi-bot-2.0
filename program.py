import discord
import tools
import emote_add
import database
import emote_detection
import traceback
from sys import stderr

async def on_ready(client: discord.Client):
    database.init()
    tools.load_emotes()
    print(f"{client.user} connected")

async def on_message(message: discord.Message):
    if not message.author.bot:
        if message.content.split(" ")[0] == "?addemote" and len(message.content.split(" ")) == 3:
            image = emote_add.get_image(message.content.split(" ")[-1])
            frames = emote_add.rescale_image(image)
            emote_add.save_image(frames, message.content.split(" ")[1])
            await message.add_reaction("✅")
        elif message.content.split(" ")[0] == "?removeemote" and len(message.content.split(" ")) == 2:
            emote_name = message.content.split(" ")[1]
            emote_add.remove_image(emote_name)
            await message.add_reaction("✅")
        else:
            # send a webhook
            try:
                await emote_detection.send_webhook(message)
            except Exception as e:
                emote_detection.webhook_updating = False
                stderr.write(traceback.format_exc())
