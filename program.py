import discord
import tools

# links: {name: link}
links = {x.split("|")[0]: x.split("|")[1] for x in open("./emoji_links.txt", "rt").readlines()}


async def on_ready(client: discord.Client):
    print(f"{client.user} connected")

# find what emote names we need
def needed_emotes(message: str):
    needed = []
    parts = message.split(":")
    for i in range(1, len(parts), 2):
        if parts[i] in links:
            needed.append(parts[i])
    return list(set(needed))

# replace the areas with their corresponding emote id
# needed_emotes: {name: id}
def replace_with_emotes(message: str, loaded_emotes: dict):
    parts = message.split(":")
    for i in range(1, len(parts), 2):
        name = parts[i]
        if name not in loaded_emotes:
            parts[i] = f":{name}:"
        elif ".gif" in links[name]:
            parts[i] = f"<a:{name}:{loaded_emotes[name]}"
        else:
            parts[i] = f"<:{name}:{loaded_emotes[name]}"
    return "".join(parts)


async def on_message(message: discord.Message):
    if not message.author.bot:

        # get the current guild
        cur_guild: discord.Guild = message.guild

        # get the emotes to replace
        needed = needed_emotes(message.content)
        if len(needed) > cur_guild.emoji_limit:
            tools.webhook_empty(
                f"Turns out the server doesn't have enough emote slots to hold your {len(needed)} emotes!")
            return

        # update emotes and get the update message
        needed_ids = await tools.add_emotes(needed, cur_guild)
        k = replace_with_emotes(message.content, needed_ids)
        print(k)

        # send the new message
        tools.webhook_imitate(k, message.author)

        # delete the original message
        await message.delete()
