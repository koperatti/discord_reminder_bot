import discord
import os
import sys
import datetime
import traceback
import random
from discord.ext import tasks
import asyncio
import unicodedata
import pprint

TOKEN = os.environ['DISCORD_BOT_TOKEN'] # discord botのトークン。Heroku上で環境変数として設定している。
DIFF_JST_FROM_UTC = 9
started_time = datetime.datetime.utcnow() + datetime.timedelta(hours=DIFF_JST_FROM_UTC) #起動した瞬間の時刻(JTC)を取得
BOT_LOG_CHANNEL = 710813437675962449 # BotlogチャンネルのID
BOT_COMMAND_CHANNEL = 710752335781036073 # コマンド送信用チャンネルのID
BOT_DATA_CHANNEL = 710752335781036073 # 課題、イベント一覧チャンネルのID
remind_list = []
day_later = 0
on_cmd_cnl = False
cmd_cnl = True
change = False
task = ''
# 以下のリストたちはbotのランダムな返信リスト。 #の部分がタスク名に置き換わる(No_hashだけはそのまま)
Format_error_deadline =['ブブー！締切の日時のフォーマットが違います',
			'ワタシ、ソノニチジ ワカラナイデス',
			'残念！締切の日時のフォーマットエラーだ！',
		        'あぁ...締め切り日時って間違える人多いんだよね...']
Element_missed = ['あれ...何かが足りない...',
		  'ブブー！ヨウソガタリナイアルヨ',
		  '要素が足りないんだよおおぉぉぉぉ！！']
No_astarisk = ['*(アスタリスク)は入れてはならない！これは当局からの命令だ！',
	       'ごめん、僕 *(アスタリスク)嫌いなんだ...',
	       '*(アスタリスク)は諸悪の根源。間違って使うとPCもぶっ飛ぶんだぜ?',
	       '君は *(アスタリスク)を使うには若すぎるよ!',
	       'すまないねぇ、うちでは *(アスタリスク)は禁止なんだよ']
No_hash = ['やめてくれ！ #はTwitterだけで十分だ！',
	   '#__ハッシュタグを使うな__',
	   '#(ハッシュ)と♯(シャープ)の違いも分からないのにハッシュを使うんじゃない！']
Too_many_elements = ['ブブー！要素が多すぎるよ',
		     '君の人生が満ち足りてても指定された以上の要素を入力する必要はないんだよ?',
		     'ゲフ...おなか一杯。そんなに要素はいらないよ']
Added = ['# を課題リストにぶっこんでやったぜ！',
	 '# は課題リストの一部となった！',
	 '# は課題リストに吸収された！',
	 '# を課題リストにシューーーーート！！超！エキサイティン！！！',
	 'シュウゥゥゥゥ... # は課題リストに吸い込まれていった！',
	 '# が課題リストに飛び乗りました',
	 '# が課題リストに滑り込みました',
	 '気をつけろ！ # が課題リストにお出ましだ！'
	 'やぁ！ #! ピザ持ってきたよね']
Removed = ['あばよ、#、お前の役目はもう終わりなんだ。',
	   '達者でな、#、またどこかで会おうぜ！',
	   'じゃあな #。Classiと共に葬り去ってやる',
	   '俺たちが再び画面を見たとき、#はもういなかった...',
	   '# はこの世から抹殺された！',
	   'お前はここにいるべきでないんだよ... #君?',
	   'いけっ、ピカチュウ、#に十万ボルトだ！']
Not_found = ['404エラー！この意味が分かるかな? #がいないってことだよ',
	     '# は迷子だ！見つからないよ！',
	     '#?そんなやついたっけな?',
	     'リスト中に#なし、を検出しました']
Same_name = [#ならもうここにおるぞ！さては偽物だな！',
	     'どうやらあなたは課題リストをよく見ていないようだねぇ、#はとっくに登録済みだよ',
	     'あれぇ?#?聴き覚えのある名前だなぁ']
Rescheduled = ['ガチャコン！ #の締め切りが変わった！']
Wrong_channel = ['そのチャンネルからは俺にその命令を下せないぜ！',
	         'その命令はここでは実行できないぜ！課題、イベント一覧に来るんだな！',
	         'そのチャンネルからはそのコマンドは実行できないぜ！']

# ↓時刻の整形をする関数。入れられた値(18-5-6_3:15等)を整形(2018-05-06_03:15等)する
def time_format_check(date):
	slash_count = date.count('/')
	coron_count = date.count(':')
	if slash_count <= 0:
		date = 'Format error'
	elif slash_count >= 3:
		date = 'Format error'
	else:
		if slash_count == 1:
			date = '2020/' + date
		elif date[2] == '/':
			date = '20' + date
		if date[4] == '/':
			if date[6] == '/':
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
			if len(date) == 16 or len(date) == 10:
				try:
					month = int(date[5:7])
					day = int(date[8:10])
					if month <= 0:
						date = 'Format error'
					elif month >= 13:
						date = 'Format error'
					elif day <= 0:
						date = 'Format error'
					elif day >= 31:
						date = 'Format error'
					else:
						pass
					if len(date) == 16:
						year = int(date[0:4])
						if year <= 0:
							date = 'Format error'
						if year >= 2024:
							date = 'Format error'
						else:
							pass
				except:
					date = 'Format error'
			else:
				date = 'Format error'
		else:
			date = 'Format error'
	return date
# rtn_msgの中の'#'をタスク名に置き換える関数
def hash_replace(task,strings):
	idx = strings.find(r'#')
	result = strings[:idx] + str(task) + strings[idx+1:]
	return result

# 文字列の長さをスペースで保管する関数
def left(digit, msg):
	for c in msg:
		if unicodedata.east_asian_width(c) in ('F', 'W', 'A'):
			digit -= 4
		elif unicodedata.east_asian_width(c) in ('Na'):
			digit -= 2
		elif unicodedata.east_asian_width(c) in ('H'):
			digit -= 2
		else:
			digit -= 2
	msg = msg + ' ' * digit
	return msg

# 二次元配列をそろえて表示するためのコマンド
def list_show(remind_list, option = ['normal']):
	remind_list_show = sorted(remind_list)
	if 'in' in option:
		dt_today = datetime.datetime.today()
		search_date = dt_today + timedelta(days=day_later, hours=DIFF_JST_FROM_UTC)
		search_date = datetime.strftime(search_date, '%Y/%m/%d')
		counter = 0
		detect = False
		for i in remind_list:
			Day = i[0]
			if not detect:
				if int(search_date[:4]) > int(Day[:4]):
					pass
				elif int(search_date[:4]) == int(Day[:4]):
					if int(search_date[6:8]) > int(Day[6:8]):
						pass
					elif int(search_date[6:8]) == int(Day[6:8]):
						if int(search_date[9:11]) >= int(Day[9:11]):
							pass
						else:
							detect = True
					else:
						detect = True
				else:
					detect = True
				counter = counter + 1
			else:
				break
		remind_list_show = remind_list[:counter]
	if 'normal' in option:
		sndmsg = 'タスク一覧\n__**締切**                              **タスク**                                                               **科目名**                  __\n'
		for a in remind_list_show:
			i = a[0]
			sndmsg = sndmsg + left(38, i)
			i = a[1]
			sndmsg = sndmsg + left(75, i)
			i = a[2]
			sndmsg = sndmsg + left(30, i)
			sndmsg = sndmsg + '\n'
	elif 'phone' in option:
		sndmsg = '**タスク一覧**\n'
		for a in remind_list_show:
			sndmsg = sndmsg + '\n'
			sndmsg = sndmsg + str(a[0]) + '\n'
			sndmsg = sndmsg + str(a[1]) + ' ('
			sndmsg = sndmsg + str(a[2]) + ')\n'
	return sndmsg

# ↓コマンドの解釈をする関数。
def list_process(message, on_cmd_cnl):
	global remind_list
	global task
	global change
	global day_later
	global cmd_cnl
	cmd_cnl = True
	change = False
	rtn_msg = ''
	log_msg = ''
	command = message.content # 入力されたメッセージを変数(command)に代入
	if '/add' in command: # /add がメッセージ内に入っているかの判別
		if on_cmd_cnl:
			if '*' not in command: # * がメッセージ内に入っていないかの判別
				if '#' not in command: # '#' がメッセージ内に入っていないかの判別
					command_list = command.split()[1:] # コマンドをスペースで区切り、/addだけ消す(例：/add task subject 2020-08-28_12:34 → task,subject,2020-08-28_12:34)
					if len(command_list) == 3: # コマンドが正しい形かどうか判別
						# ↓コマンドの引数の分解 タスクの名前、科目、締め切りをそれぞれの変数に代入(締め切りは前にある時刻の整形関数に通されてから代入)
						task_name = command_list[0]
						subject = command_list[1]
						deadline = time_format_check(command_list[2])
						# ↓同じ名前がないかチェック。あったら変数detectを真にし、場所を変数counterに代入
						counter = 0
						detect = False
						for i in remind_list:
							if task_name == i[1]:
								detect = True
								break
							counter = counter + 1
						# 同じ名前があったらその旨を変数(rtn_msg)に格納
						if detect:
							task = task_name
							rtn_msg = random.choice(Same_name)
							rtn_msg = hash_replace(task, rtn_msg)
						# 締切の書き方がおかしかったらその旨を変数(rtn_msg)に格納
						elif deadline == 'Format error':
							rtn_msg = random.choice(Format_error_deadline)
						else:
							# なにもおかしいところがなかったらリスト(remind_list)にタスクを追加
							remind_list.append([deadline, task_name, subject])
							print(str(message.author) + 'add ' + str(deadline) + ' ' + str(task_name) + ' ' + str(subject))
							task = str(task_name)
							# タスクが追加された旨を変数(rtn_msg)に格納
							rtn_msg = random.choice(Added)
							rtn_msg = hash_replace(task, rtn_msg)
							# 課題リスト(remind_list)が変更されたことを示すために変数(change)を真にする
							change = True
					elif len(command_list) >= 4:
						# 引数が多すぎた場合、その旨を変数(rtn_msg)に格納
						rtn_msg = random.choice(Too_many_elements)
					elif len(command_list) <= 2:
						# 引数が足りない場合、その旨を変数(rtn_msg)に格納
						rtn_msg = random.choice(Element_missed)
				else:
					# '#'が使われている場合、その旨を変数(rtn_msg)に格納
					rtn_msg = random.choice(No_hash)
			else:
				# *が使われている場合、その旨を変数(rtn_msg)に格納
				rtn_msg = random.choice(No_astarisk)
		else:
			rtn_msg = random.choice(Wrong_channel)
	elif '/remove' in command: # /remove がメッセージ内に入っているかの判別
		cmd_cnl = True
		if on_cmd_cnl:
			command_list = command.split()[1:] # コマンドをスペースで区切り、/removeだけ消す(例：/remove task → task)
			if len(command_list) == 1: # コマンドが正しい形かどうか判別
				counter = 0
				detect = False
				# 引数に該当するタスク名を課題リストから検索、あったら変数detectを真にし、場所を変数counterに代入
				for i in remind_list:
					if command_list[0] == i[1]:
						detect = True
						break
					counter = counter + 1
				if detect:
					# あった場合、削除し、削除したタスク名を変数(task)に代入
					task = remind_list.pop(counter)[1]
					print(str(message.author) + 'removed the ' + str(task))
					# タスクを削除した旨を変数(rtn_msg)に格納
					rtn_msg = random.choice(Removed)
					rtn_msg = hash_replace(task, rtn_msg)
					# リストが変更されたことを示すために変数(change)を真にする
					change = True
				else:
					# なかった場合、見つからなかった旨を変数(rtn_msg)に格納
					task = str(command_list[0])
					rtn_msg = random.choice(Not_found)
					rtn_msg = hash_replace(task, rtn_msg)
			else:
				# その他の場合、要素が多すぎる旨を変数(rtn_msg)に代入
				rtn_msg = random.choice(Too_many_elements)
		else:
			cmd_cnl = False
			rtn_msg = random.choice(Wrong_channel)
	elif '/list' in command:
		global day_later
		command_list = command.split()[1:]
		option = []
		cmd_cnl = False
		if command_list:
			if 'phone' in command:
				option.append('phone')
			if 'in_today' in command:
				day_later = 0
				option.append('in')
			elif 'in_tommorow' in command:
				day_later = 1
				option.append('in')
			elif 'in' in command:
				try:
					day_later = int(command[command.index('in') + 1])
					option.append('in')
				except:
					day_later = 'Error'
					rtn_msg = random.choice(Element_missed)
			if not day_later == 'Error':
				rtn_msg = list_show(remind_list, option)
		else:
			rtn_msg = list_show(remind_list)

		print(str(message.author) + ' used /list')	
	elif '/reschedule' in command:
		cmd_cnl = False
		if on_cmd_cnl:
			command_list = command.split()[1:]
			if len(command_list) >= 3:
				# 引数が多すぎた場合、その旨を変数(rtn_msg)に格納
				rtn_msg = random.choice(Too_many_elements)
			elif len(command_list) <= 1:
				# 引数が足りない場合、その旨を変数(rtn_msg)に格納
				rtn_msg = random.choice(Element_missed)
			else:
				counter = 0
				detect = False
				# 引数に該当するタスク名を課題リストから検索、あったら変数detectを真にし、場所を変数counterに代入
				for i in remind_list:
					if command_list[0] == i[1]:
						detect = True
						break
					counter = counter + 1
				if detect:
					new_schedule = time_format_check(command_list[1])
					if deadline == 'Format error':
						rtn_msg = random.choice(Format_error_deadline)
					else:
						remind_list[counter][0] = new_schedule
						task = remind_list[counter][1]
						rtn_msg = random.choice(Rescheduled)
						rtn_msg = hash_replace(task, rtn_msg)
						print(str(message.author) + ' rescheduled ' + str(task))
						cmd_cnl = True
						change = True
		else:
			cmd_cnl = False
			rtn_msg = random.choice(Wrong_channel)
	return rtn_msg, cmd_cnl

# 接続に必要なオブジェクトを生成
client = discord.Client()
# チャンネルIDからチャンネルオブジェクトを作成
log_channel = client.get_channel(BOT_LOG_CHANNEL)
command_channel = client.get_channel(BOT_COMMAND_CHANNEL)
data_channel = client.get_channel(BOT_DATA_CHANNEL)
change = False

# 起動時に動作する処理
@client.event
async def on_ready():
	global remind_list
	log_channel = client.get_channel(BOT_LOG_CHANNEL)
	data_channel = client.get_channel(BOT_DATA_CHANNEL)
	# botlogに再起動した旨を送信
	await log_channel.send(str(started_time) + '(JST) Bot restarted!')
	# 自分のステータスを変更
	await client.change_presence(activity=discord.Game(name='課題リマインディング'))
	async for message in data_channel.history():
		content = message.content
		memory_list = content.split('\n')[2:]
		for z in memory_list:
			splited = z.split()
			remind_list.append(splited)
	await log_channel.send('Imported the data from 課題、イベント一覧!')
	print(remind_list)
	print('\n\nimport complete!')

# メッセージ受信時に動作する処理
@client.event
async def on_message(message):
	global remind_list
	global change
	global on_cmd_cnl
	try:
		command_channel = client.get_channel(BOT_COMMAND_CHANNEL)
		# メッセージ送信者がBotだった場合は無視する
		if message.author.bot:
			return
		if message.channel == command_channel:
			on_cmd_cnl = True
		else:
			on_cmd_cnl = False
		# 先ほどのコマンドを解釈し、実行する関数にメッセージ内容を入れて実行し、返り値rtn_msgを得る
		rtn_msg, cmd_chl = list_process(message, on_cmd_cnl)
		if cmd_chl:
			if rtn_msg: # rtn_msgに何か書いていたらそれをコマンド送信用チャンネルに送信
				remind_list = sorted(remind_list)
				sndmsg = list_show(remind_list, option='normal')
				data_channel = client.get_channel(BOT_DATA_CHANNEL)
				def is_me(m):
					return m.author == client.user
				await data_channel.purge(limit=100)
				await data_channel.send(sndmsg)
				await command_channel.send(rtn_msg)
				await asyncio.sleep(5)
				await data_channel.purge(limit=100, check=is_me)
				await data_channel.send(sndmsg)
				change = False
		else:
			if rtn_msg:
				await message.channel.send(rtn_msg)
	except: # 何かエラーが起きたらその内容をbotlogチャンネルに送信
		log_channel = client.get_channel(BOT_LOG_CHANNEL)
		exc_type, exc_obj, exc_tb = sys.exc_info()
		await log_channel.send('Error in line ' + str( exc_tb.tb_lineno ) + ' in ' +str(os.path.split( exc_tb.tb_frame.f_code.co_filename )[ 1 ]))
		await log_channel.send(str(sys.exc_info()[0]))
		await log_channel.send(str(sys.exc_info()[1]))
		await log_channel.send(str(sys.exc_info()[2]))

# Botの起動とDiscordサーバーへの接続
client.run(TOKEN)
