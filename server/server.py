from flask import Flask, jsonify, request, redirect, send_file
from threading import Thread
import json

import vbox, config
from config import VM

app = Flask('internal_server')

tasks = []
logs = []

@app.route('/get_task')
def get_task():
	if len(tasks) == 0:
		return ''
	return jsonify(tasks.pop(0))

@app.route('/put_log', methods=['GET', 'POST'])
def put_log():
	log = request.values.get('log')
	log = log.replace('\t', '    ')
	logs.append(log)
	if len(logs) > 500:
		logs.pop(0)
	return 'ok'

Thread(target=lambda:app.run(host='10.89.40.1', port=1561)).start()

app = Flask('external_server')

@app.route('/put_task', methods=['GET', 'POST'])
def put_task():
	if request.cookies.get('token') != config.TOKEN:
		return ''
	task = json.loads(request.values.get('task'))
	tasks.append(task)
	return 'ok'

@app.route('/tasks')
def get_tasks():
	if request.cookies.get('token') != config.TOKEN:
		return ''
	return jsonify(tasks)

@app.route('/logs')
def get_logs():
	if request.cookies.get('token') != config.TOKEN:
		return ''
	return '<pre>' + '<br>'.join(logs) + '</pre>'

@app.route('/startvm')
def start_vm():
	vbox.start_vm(VM)
	return redirect('/')

@app.route('/stopvm')
def stop_vm():
	vbox.stop_vm(VM)
	return redirect('/')

@app.route('/screenshot')
def screenshot():
	vbox.take_screenshot(VM, 'tmp.png')
	return send_file('tmp.png')

@app.route('/joinmeet')
def join_meet():
	id = request.values.get('id')
	pwd = request.values.get('pwd')
	if pwd == '':
		pwd = None
	id = id.replace(' ', '')
	tasks.append({'type': 'join_meet', 'meet_id': int(id), 'meet_pwd': pwd})
	return redirect('/?id=%s&pwd=%s' % (id, pwd if pwd else ''))

@app.route('/add/<x>')
def add(x):
	tasks.append({'type': x})
	return redirect('/')

@app.route('/stat')
def stat():
	res = '<script>setTimeout(function(){location.reload()}, 5000)</script>'
	res += 'VM Status: ' + vbox.get_status(VM) + '<br>\n'
	res += '<br>Tasks:<br>\n'
	res += '<pre>' + json.dumps(tasks) + '</pre>'
	res += '<br>Recent logs:<br>\n'
	res += '<pre>' + '<br>'.join(logs[max(0, len(logs) - 50):]) + '</pre>'
	return res

@app.route('/')
def index():
	print(request.cookies.get('token') , config.TOKEN)
	if request.cookies.get('token') != config.TOKEN:
		return ''
	id = request.values.get('id') or ''
	pwd = request.values.get('pwd') or ''
	assert id == '' or id.isnumeric()
	assert pwd == '' or pwd.isnumeric()
	res = '<body style="overflow:hidden">'
	res += '<a href="/startvm">Start VM</a> '
	res += '<a href="/stopvm">Stop VM</a> '
	res += '<a href="/screenshot">Screenshot</a> '
	res += '<a href="/logs">Full logs</a> '
	res += '<br>'
	res += '''<form action="/joinmeet">
	Join meet:
	<input placeholder="meet id" name="id" value="%s">
	<input placeholder="meet password" name="pwd" value="%s">
	<input type="submit">
</form>''' % (id, pwd)
	actions = ['start_wemeet', 'kill_wemeet', 'switch_mode', 'left_meet', 'start_ffmpeg', 'stop_ffmpeg']
	for i in actions:
		res += '<a href="/add/%s">%s</a> ' % (i, i)
	res += '<br><br><br>\n'
	res += '<iframe src="/stat" style="width:100%;height:100%;border:0"></iframe>'
	res += '</body>'
	return res

app.run(host='127.0.0.1', port=1562)
