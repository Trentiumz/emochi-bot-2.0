import discord
import program
import tools

client = discord.Client()

# passing the events onto the program
@client.event
async def on_ready():
    global client
    await program.on_ready(client)

@client.event
async def on_message(message):
    await program.on_message(message)

# start a flask server
token = tools.lines["token"]

# start the client
client.run(token)