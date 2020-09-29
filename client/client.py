import os, time, json, random, datetime, requests, traceback, subprocess
import win32api, win32com, win32com.client
from win32api import *
from win32gui import *
from win32con import *
from win32process import *
import ctypes


URL = 'some api endpoint'
os.chdir('directory of this file')


def pushlog(s, s2=None):
	if s2 is not None:
		s += ' ' + str(s2)
	for i in range(3):
		try:
			requests.post(URL + '/put_log', data={'log': s}, timeout=10)
			return
		except:
			pass


def get_wemeet_window(req_title):
	ps = EnumProcesses()
	pids = []
	for pid in ps:
		try:
			hp = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, True, pid)
			fn = GetModuleFileNameEx(hp, 0)
			if fn.endswith('wemeetapp.exe'):
				pids.append(pid)
		except Exception as e:
			pass

	ws = []
	cur = ctypes.windll.user32.GetTopWindow(None)
	while True:
		nxt = GetWindow(cur, GW_HWNDNEXT)
		if not nxt:
			break
		tid, pid = GetWindowThreadProcessId(nxt)
		title = GetWindowText(nxt)
		if pid in pids and req_title in title:
			ws.append(nxt)
		cur = nxt
	return ws


def click(hwnd, x, y):
	a = SendMessage(hwnd, WM_LBUTTONDOWN, 1, x | y << 16)
	b = SendMessage(hwnd, WM_LBUTTONUP, 0, x | y << 16)
	return a, b


def join_meet(meet_id, meet_pwd, join_name):
	ws = get_wemeet_window('腾讯会议')
	assert len(ws) <= 2
	pushlog('hwnd of wemeet:', ws)

	for i in ws:
		click(i, 56, 123)

	time.sleep(0.5)
	ws2 = get_wemeet_window('腾讯会议')
	ws2_all = get_wemeet_window('')
	ws2 = set(ws2) - set(ws)
	assert len(ws2) == 1
	ws2 = list(ws2)
	pushlog('hwnd of join meet:', ws2[0])

	for i in str(meet_id):
		time.sleep(0.1)
		SendMessage(ws2[0], WM_CHAR, ord(i), 0)
	click(ws2[0], 336, 178)
	time.sleep(0.1)
	click(ws2[0], 72, 177)
	for i in join_name:
		time.sleep(0.1)
		SendMessage(ws2[0], WM_CHAR, ord(i), 0)
	time.sleep(0.1)
	click(ws2[0], 193, 616)

	if meet_pwd is not None:
		time.sleep(2)
		ws3 = get_wemeet_window('')
		ws3 = set(ws3) - set(ws2_all)
		#assert len(ws3) <= 3
		ws3 = list(ws3)
		pushlog('hwnd of password:', ws3)
		for i in ws3:
			try:
				left, top, right, bottom = GetWindowRect(i)
				if bottom - top > 500 or right - left > 600:
					continue
				click(i, 62, 96)
				for j in meet_pwd:
					time.sleep(0.1)
					SendMessage(i, WM_CHAR, ord(j), 0)
				time.sleep(0.1)
				click(i, 259, 162)
			except Exception as e:
				pushlog('error at trying password:', e)
				pass

	time.sleep(2)
	ws3 = get_wemeet_window('')
	ws3 = set(ws3) - set(ws2_all)
	pushlog('hwnd of select audio:', ws3)
	for i in ws3:
		click(i, 256, 284)

	time.sleep(2)
	ws4 = get_wemeet_window('腾讯会议')
	ws4 = set(ws4) - set(ws2_all)
	pushlog('hwnd of select meet:', ws4)
	real = []
	for i in ws4:
		left, top, right, bottom = GetWindowRect(i)
		if bottom - top <= 100 or right - left <= 500:
			continue
		click(i, 156, 609)
		click(i, 935, 58)
		shell = win32com.client.Dispatch("WScript.Shell")
		shell.SendKeys('%')
		SetForegroundWindow(i)
		time.sleep(0.1)
		real.append(i)
	assert len(real) == 1
	return real[0]


def switch_mode(hwnd):
	shell = win32com.client.Dispatch("WScript.Shell")
	shell.SendKeys('%')
	SetForegroundWindow(hwnd)

	SendMessage(hwnd, WM_KEYDOWN, VK_ESCAPE, 0)
	SendMessage(hwnd, WM_KEYUP, VK_ESCAPE, 0)

	click(hwnd, 156, 609)
	click(hwnd, 935, 58)
	shell = win32com.client.Dispatch("WScript.Shell")
	shell.SendKeys('%')
	SetForegroundWindow(hwnd)
	time.sleep(0.1)

	left, top, right, bottom = GetWindowRect(hwnd)
	click(hwnd, right - 76, 11)


def left_meet(hwnd):
	shell = win32com.client.Dispatch("WScript.Shell")
	shell.SendKeys('%')
	SetForegroundWindow(hwnd)

	SendMessage(hwnd, WM_KEYDOWN, VK_ESCAPE, 0)
	SendMessage(hwnd, WM_KEYUP, VK_ESCAPE, 0)

	x, y = 948, 25
	PostMessage(hwnd, WM_LBUTTONDOWN, 1, x | y << 16)
	PostMessage(hwnd, WM_LBUTTONUP, 0, x | y << 16)
	time.sleep(0.5)
	ws = get_wemeet_window('')
	pushlog('hwnd of all windows:', ws)
	for i in ws:
		if GetWindowText(i) == '':
			click(i, 272, 162)


def start_wemeet():
	os.system('"C:\\Program Files (x86)\\Tencent\\WeMeet\\wemeetapp.exe"')
	time.sleep(10)
	ws = get_wemeet_window('')
	pushlog('hwnd of all windows:', ws)
	for i in ws:
		if GetWindowText(i) == '':
			click(i, 166, 160)


def kill_wemeet():
	os.system('taskkill -im wemeetapp.exe -f')


ffmpeg_path = 'path of ffmpeg.exe'
out_path = 'video output path'


def start_ffmpeg():
	fn = datetime.datetime.now().strftime('%Y-%m-%d %H.%M.%S.mkv')
	#p = subprocess.Popen([ffmpeg_path, '-f', 'gdigrab', '-framerate', '24', '-i', 'desktop', '-f', 'dshow', '-i', 'audio=virtual-audio-capturer', out_path + fn])
	p = subprocess.Popen('%s -f gdigrab -framerate ntsc -i desktop -f dshow -i audio="virtual-audio-capturer" -c:a aac "%s"' % (ffmpeg_path, out_path + fn), shell=True)
	return p


def stop_ffmpeg(p):
	p.kill()
	os.system('taskkill -im ffmpeg.exe -f')


cnt = 0
while True:
	try:
		s = requests.get(URL + '/get_task', timeout=10).text
	except:
		s = ''
	if s == '':
		time.sleep(2)
		cnt += 1
		if cnt % 30 == 0:
			pushlog('heartbeat:', time.time())
		continue
	try:
		s = json.loads(s)
		pushlog('working:', s)
		if s['type'] == 'start_wemeet':
			start_wemeet()
		elif s['type'] == 'join_meet':
			assert s['meet_pwd'] is None or s['meet_pwd'].isnumeric()
			join_name = 'your name'
			hwnd = join_meet(int(s['meet_id']), s['meet_pwd'], join_name)
		elif s['type'] == 'switch_mode':
			switch_mode(hwnd)
		elif s['type'] == 'left_meet':
			left_meet(hwnd)
		elif s['type'] == 'kill_wemeet':
			kill_wemeet()
		elif s['type'] == 'start_ffmpeg':
			p = start_ffmpeg()
		elif s['type'] == 'stop_ffmpeg':
			stop_ffmpeg(p)
		elif s['type'] == 'shutdown':
			os.system('shutdown -s -t 0')
		else:
			pushlog('unknown operation')
		pushlog('done')
	except:
		pushlog(traceback.format_exc().replace('\n', '<br>'))
