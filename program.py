import discord
import emote_detection
import tools

# links: {name: link}
links = {x.split("|")[0]: x.split("|")[1].rstrip()for x in open("./emoji_links.txt", "rt").readlines()}

# list of emotes but formatted for regex
emotes = [f":{s}:" for s in links]

# a regex for which we can find all of the possible emotes
regex_for_emotes = "|".join(emotes)
print(regex_for_emotes)


async def on_ready(client: discord.Client):
    print(f"{client.user} connected")

async def on_message(message: discord.Message):
    if not message.author.bot:

        # get the current guild
        cur_guild: discord.Guild = message.guild

        # get the emotes to replace, all just pure names of the emotes
        needed = list(emote_detection.needed_emotes(message.content, regex_for_emotes))

        # if he needs too many emotes, then boop we quit it
        if len(needed) > cur_guild.emoji_limit:
            tools.webhook_empty(
                f"Turns out the server doesn't have enough emote slots to hold your {len(needed)} emotes!")
            return

        # send a webhook
        await emote_detection.send_webhook(needed, cur_guild, message, links)

        # delete the original message
        await message.delete()
