from threading import Thread
import discord
import flask
import program

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
token = program.tools.lines[0].split(": ")[1]

app = flask.Flask("Starting app")
def run():
    app.run(host="0.0.0.0", port=8080)

t = Thread(target=run)
t.start()

# start the client
client.run(token)