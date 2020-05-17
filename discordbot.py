import discord
import os
import sys
import datetime
import traceback
from discord.ext import tasks
import asyncio

TOKEN = os.environ['DISCORD_BOT_TOKEN']
DIFF_JST_FROM_UTC = 9
started_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
BOT_LOG_CHANNEL = 710813437675962449
BOT_COMMAND_CHANNEL = 710335701459271799
BOT_DATA_CHANNEL = 710752335781036073
remind_list = []
remind_list_old = []

# ↓時刻の整形をする関数
def time_format_check(date):
	hifun_count = date.count('-')
	coron_count = date.count(':')
	if not hifun_count == 2:
		date = 'Format error'
	else:
		if date[2] == '-':
			date = '20' + date
		if date[4] == '-':
			if date[6] == '-':
				date = date[:5] + '0' + date[5:]
			if len(date) == 10:
				pass
			elif len(date) == 9:
				date = date[:8] + '0' + date[8:]
			elif date[9] == '_':
				date = date[:8] + '0' + date[8:]
				if date[12] == ':':
					date = date[:11] + '0' + date[11:]
				if len(date) == 15:
					date = date[:14] + '0' + date[14:]
		else:
			date = 'Format error'
	return date

# ↓コマンドの解釈をする関数
def list_process(message):
	global remind_list
	rtn_msg = ''
	log_msg = ''
	command = message.content
	if '/add' in command:
		if '*' not in command:
			command_list = command.split()[1:]
			if len(command_list) == 3:
				task_name = command_list[0]
				subject = command_list[1]
				deadline = time_format_check(command_list[2])
				counter = 0
				detect = False
				for i in remind_list:
					if task_name == i[0]:
						detect = True
						break
					counter = counter + 1
				if detect:
					rtn_msg = 'Same name detected! Try with other name.'
				elif deadline == 'Format error':
					rtn_msg = 'Format error in deadline'
				else:
					remind_list.append([task_name, subject, deadline])
					rtn_msg =  'Added ' + str(task_name) + ',' + str(subject) + ',' + str(deadline)
			else:
				rtn_msg = 'Some element missed'
		else:
			rtn_msg = 'You can not use * in the statement'
	elif '/remove' in command:
		command_list = command.split()[1:]
		if len(command_list) == 1:
			counter = 0
			detect = False
			for i in remind_list:
				if command_list[0] == i[0]:
					detect = True
					break
				counter = counter + 1
			if detect:
				rtn_msg = 'Deleted ' + remind_list.pop(counter)[0] 
			else:
				rtn_msg = 'could not find ' + str(command_list[0])
		else:
			rtn_msg = 'Too many elements'
	return rtn_msg

# 接続に必要なオブジェクトを生成
client = discord.Client()
log_channel = client.get_channel(BOT_LOG_CHANNEL)
command_channel = client.get_channel(BOT_COMMAND_CHANNEL)
data_channel = client.get_channel(BOT_DATA_CHANNEL)

# 起動時に動作する処理
@client.event
async def on_ready():
	log_channel = client.get_channel(BOT_LOG_CHANNEL)
	await log_channel.send(str(started_time) + '(JST) Bot restarted!')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
	try:
		# メッセージ送信者がBotだった場合は無視する
		if message.author.bot:
			return
		rtn_msg = list_process(message)
		command_channel = client.get_channel(BOT_COMMAND_CHANNEL)
		await command_channel.send(rtn_msg)
	except:
		log_channel = client.get_channel(BOT_LOG_CHANNEL)
		await log_channel.send(str(sys.exc_info()))
# 一分に一回行う処理
@tasks.loop(seconds=60)
async def loop():
	global remind_list_old
	sndmsg = '\n'
	if remind_list_old == remind_list:
		pass
	else:
		remind_list_old = remind_list
		for a in remind_list:
			for i in a:
				sndmsg = sndmsg + '   ' + str(i)
			sndmsg = sndmsg + '\n'
		
		data_channel = client.get_channel(BOT_DATA_CHANNEL)
		msgs = [msg async for msg in client.logs_from(data_channel, limit=20)]
		await client.delete_messages(msgs)
		await data_channel.send(sndmsg)
loop.start()
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
