from discord.ext import commands
import os
import datetime
import traceback

token = os.environ['DISCORD_BOT_TOKEN']
started_time = datetime.datetime.today().strftime("%Y/%m/%d/%H/%M/%S")
client = discord.Client()
TOKEN = "<Token>"

@client.event
async def on_ready():

    ch_name = "710813437675962449"

    for channel in client.get_all_channels():
        if channel.name == ch_name:
            await channel.send(str(started_time) + " Bot restarted")

client.run(TOKEN)
