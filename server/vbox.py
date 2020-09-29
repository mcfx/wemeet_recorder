import subprocess

def get_status(vm):
	p = subprocess.Popen(['VBoxManage', 'showvminfo', vm], stdout = subprocess.PIPE)
	s, _ = p.communicate()
	s = s.decode()
	s = s[s.find('State: ') + 10:]
	return s[:s.find('\n')].strip()

def start_vm(vm):
	subprocess.run(['VBoxManage', 'startvm', vm, '--type', 'headless'])

def stop_vm(vm):
	subprocess.run(['VBoxManage', 'controlvm', vm, 'acpipowerbutton'])

def take_screenshot(vm, fn):
	subprocess.run(['VBoxManage', 'controlvm', vm, 'screenshotpng', fn])
