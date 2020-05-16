import discord
import os
import datetime
import traceback

TOKEN = os.environ['DISCORD_BOT_TOKEN']
DIFF_JST_FROM_UTC = 9
started_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC)
BOT_LOG_CHANNEL = 710813437675962449
BOT_COMMAND_CHANNEL = 710335701459271799
BOT_DATA_CHANNEL = 710752335781036073

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
# 接続に必要なオブジェクトを生成
client = discord.Client()
remind_list = []

# 起動時に動作する処理
@client.event
async def on_ready():
	channel = client.get_channel(BOT_LOG_CHANNEL)
	command_channel = client.get_channel(BOT_COMMAND_CHANNEL)
	data_channel = client.get_channel(BOT_DATA_CHANNEL)
	await channel.send(str(started_time) + '(JST) Bot restarted!')	



# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
	# メッセージ送信者がBotだった場合は無視する
	if message.author.bot:
		return
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
					await command_channel.send('Same name detected! Try with other name.')
				elif deadline == 'Format error':
					await command_channel.send('Format error in deadline')
				else:
					remind_list.append([task_name, subject, deadline])
			else:
				await command_channel.send('Some element missed')
		else:
			await command_channel.send('You can not use * in the statement')
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
				log_msg = remind_list.pop(counter)[0] + 'deleted'
				await channel.send(log_msg)
			else:
				await command_channel.send('could not find ' + str(command_list[0]))
		else:
			await data_channel.send('Too many elements')
	sndmsg = ''
	for a in remind_list:
		for i in a:
			sndmsg = sndmsg + ' ' + str(i)
		sndmsg = sndmsg + '\n'
	await data_channel.send(sndmsg)
	await command_channel.send(remind_list)
	# 「/neko」と発言したら「にゃーん」が返る処理
	if message.content == '/neko':
		await message.channel.send('にゃーん')

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
