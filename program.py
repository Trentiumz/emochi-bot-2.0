import discord
import tools


async def on_ready(client: discord.Client):
    print(f"{client.user} connected")


async def on_message(message: discord.Message):
    if not message.author.bot:
        # get the current guild
        cur_guild: discord.Guild = message.guild
        if len(cur_guild.emojis) == 0:
            tools.webhook_empty("unfortunately, I couldn't find a server emotes!")
            return

        # get the emote to replace
        scapegoat: discord.Emoji = cur_guild.emojis[0]
        name: str = scapegoat.name

        # get the old image
        old_image: bytes = await scapegoat.url.read()
        new = await tools.replace_emote(scapegoat, name, open("./scap.png", "rb").read())

        tools.webhook_imitate(message.content + f"<:{new.name}:{new.id}>", message.author)

        # delete the original message
        await message.delete()

        # move back to the original emote
        await tools.replace_emote(new, name, old_image)
