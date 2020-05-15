from discord.ext import commands
import os
import datetime
import traceback

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']
started_time = datetime.datetime.now()
@client.event
async def on_ready():

    ch_name = "710813437675962449"

    for channel in client.get_all_channels():
        if channel.name == ch_name:
            await channel.send(str(started_time) + "Bot restarted")
@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.command()
async def meow(ctx):
    await ctx.send('にゃーごろごろ')

@bot.command()
async def whatdoyouthink(ctx):
    await ctx.send('うん！そう思うよ！')

@bot.command()
async def goodbyebot(ctx):
    await ctx.send('悲しいなぁ')

bot.run(token)
