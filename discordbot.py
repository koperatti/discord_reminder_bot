from discord.ext import commands
import os
import datetime
import traceback

bot = commands.Bot(command_prefix='/')
token = os.environ['DISCORD_BOT_TOKEN']
started_time = datetime.datetime.now()

ctx.send(710813437675962449, str(started_time) + "Bot restarted")
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
