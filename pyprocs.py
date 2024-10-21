#!/usr/bin/python3

import psutil

# p = [f'pid:{k.pid} status:{k.status} {psutil.Process(k.pid).name()}' for k in psutil.net_connections(kind='all')]
# [k for k in p]
def get_conns():
	conns = psutil.net_connections(kind='inet')
	for k in conns:
		if k.status == 'LISTEN' or k.status == 'ESTABLISHED' or k.status == 'CLOSE_WAIT' or k.status == 'NONE':
			if k.status == 'ESTABLISHED':
				kraddr = k.raddr.ip
			else:
				kraddr = '-'
			procname = psutil.Process(k.pid).name()
			if k.pid is None:
				kpid = '-'
			else:
				kpid = k.pid
			if k.laddr.ip == '::':
				kladdrip = '0.0.0.0'
			else:
				kladdrip = k.laddr.ip
			print(f'l:{kladdrip:<13}:{k.laddr.port:<5} {procname} pid:{kpid} s:{k.status} {kraddr}')

def get_listeners():
	conns = psutil.net_connections(kind='inet')
	return sorted(set([(k.laddr.port, k.pid, k.laddr.ip, psutil.Process(k.pid).name()) for k in conns if k.status == 'LISTEN']))

if __name__ == '__main__':
	listeners = get_listeners()
	for k in listeners:
		print(f'port: {k}')
