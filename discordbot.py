import discord
from discord.ext import commands
import os
import datetime
import traceback

TOKEN = os.environ['DISCORD_BOT_TOKEN']
started_time = datetime.datetime.today().strftime("%Y/%m/%d/%H/%M/%S")
BOT_LOG_CHANNEL = '710813437675962449'

# 接続に必要なオブジェクトを生成
client = discord.Client()

# 起動時に動作する処理
@client.event
async def on_ready():
	channel = client.get_channel(CHANNEL_ID)
    await message.channel.send(str(started_time) + ' Bot restarted!')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
    # メッセージ送信者がBotだった場合は無視する
    if message.author.bot:
        return
    # 「/neko」と発言したら「にゃーん」が返る処理
    if message.content == '/neko':
        await message.channel.send('にゃーん')

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
