import discord
import os
import sys
import datetime
import traceback
import random
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
task = ''
Format_error_deadline =['ブブー！締切の日時のフォーマットが違います',
			'ワタシ、ソノニチジ ワカラナイデス',
			'残念！締切の日時のフォーマットエラーだ！']
Element_missed = ['あれ...何かが足りない...',
		  'ブブー！ヨウソガタリナイアルヨ',
		  '要素が足りないんだよおおぉぉぉぉ！！']
No_astarisk = ['*(アスタリスク)は入れてはならない！これは当局からの命令だ！',
	       'ごめん、僕 *(アスタリスク)嫌いなんだ...',
	       '*(アスタリスク)は諸悪の根源。間違って使うとPCもぶっ飛ぶんだぜ?',
	       '君は *(アスタリスク)を使うには若すぎるよ!'
	       'すまないねぇ、うちでは *(アスタリスク)は禁止なんだよ']
Too_many_elements = ['ブブー！要素が多すぎるよ',
		     '君の人生が満ち足りてても指定された以上の要素を入力する必要はないよ?',
		     'ゲフ...おなか一杯']
Added = [str(task) + ' を課題リストにぶっこんでやったぜ！',
	 str(task) + ' は課題リストの一部となった！',
	 str(task) + ' は課題リストに吸収された！',
	 str(task) + ' を課題リストにシューーーーート！！超！エキサイティン！！！',
	 'シュウゥゥゥゥ... ' + str(task) + ' は課題リストに吸い込まれていった！']
Removed = ['あばよ、' + str(task) + '、お前の役目はもう終わりなんだ、 ',
	   '達者でな、' + str(task) + '、またどこかで会おうぜ！',
	   '俺たちが再び画面を見たとき、 ' + str(task) + 'はもういなかった...',
	   str(task) + 'はこの世から抹殺された！',
	   'お前は生まれるべきでなかったんだよ... ' + str(task) + '君?',
	   'いけっ、ピカチュウ、 ' + str(task) + 'に十万ボルトだ！']
Not_found = ['404エラー！この意味が分かるかな?',
	     str(task) + ' は迷子だ！見つからないよ！',
	     str(task) + '?そんなやついたっけな?']
Same_name = [str(task) + 'ならもうここにおるぞ！さては偽物だな！',
	     'どうやらあなたは課題リストをよく見ていないようだねぇ、' + str(task) + 'はとっくに登録済みだよ',
	     '君の名は?\n' + str(task) + '。\nえっ、同じだ！']

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
					task = task_name
					rtn_msg = random.choice(Same_name)
				elif deadline == 'Format error':
					rtn_msg = random.choice(Format_error_deadline)
				else:
					remind_list.append([task_name, subject, deadline])
					task = str(task_name)
					rtn_msg = random.choice(Added)
			elif len(command_list) >= 4:
				rtn_msg = random.choice(Too_many_elements)
			elif len(command_list) <= 2:
				rtn_msg = random.choice(Element_missed)
		else:
			rtn_msg = random.choice(No_astarisk)
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
				task = remind_list.pop(counter)[0]
				rtn_msg = random.choice(Removed)
			else:
				task = str(command_list[0])
				rtn_msg = random.choice(Not_found) 
		else:
			rtn_msg = random.choice(Too_many_elements)
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
		if rtn_msg:
			await command_channel.send(rtn_msg)
	except:
		log_channel = client.get_channel(BOT_LOG_CHANNEL)
		await log_channel.send(str(sys.exc_info()))
# 一分に一回行う処理
@tasks.loop(seconds=10)
async def loop():
	try:
		global remind_list_old
		sndmsg = '\n'
		if remind_list_old == remind_list:
			pass
		else:
			for a in remind_list:
				for i in a:
					sndmsg = sndmsg + '   ' + str(i)
				sndmsg = sndmsg + '\n'
			remind_list_old = remind_list
			data_channel = client.get_channel(BOT_DATA_CHANNEL)
			await data_channel.purge()
			await data_channel.send(sndmsg)
	except:
		log_channel = client.get_channel(BOT_LOG_CHANNEL)
		await log_channel.send(str(sys.exc_info()))
loop.start()
# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
