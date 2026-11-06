import os
import sys
import glob
import pathlib
# pid = sys.argv[1]

def hexip2str(hexip):
	return '.'.join([str(int('0x' + hexip[j:j+2],16)) for j in range(6,-2,-2)])

proclist = list(glob.glob('/proc/**/net/tcp',recursive=False))
tcpconns = [
	{'pid': pathlib.Path(k).parts[2],
	'cmdline': open(f'/proc/{pathlib.Path(k).parts[2]}/cmdline','r').read() if pathlib.Path(f'/proc/{pathlib.Path(k).parts[2]}/cmdline').exists() else '',
	'tcp': open(k,'r').readlines()
	}
	for k in proclist if pathlib.Path(k).exists()]

# tcpconn = open(f'/proc/{pid}/net/tcp','r').readlines()


for tcpconn in tcpconns:
	print(f'PID: {tcpconn["pid"]}, CMDLINE: {tcpconn["cmdline"]}')
	for conn in tcpconn['tcp']:
		str_conn = [x.strip() for x in conn.replace(':',' ').split()]
		if str_conn[0].isalpha():
			continue
		local_ip = hexip2str(str_conn[1])
		local_port = str(int(str_conn[2],16))
		remote_ip = hexip2str(str_conn[3])
		remote_port = str(int(str_conn[4],16))
		if remote_ip == '0.0.0.0':
			continue
		print(f'{local_ip}:{local_port} => {remote_ip}:{remote_port}')
		# print(hexip2str(str_conn[1]) + ':' + str(int(str_conn[2],16)),' => ',hexip2str(str_conn[3]) + ':' + str(int(str_conn[4],16)))


