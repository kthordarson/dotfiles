#!/usr/bin/python3
import re
from loguru import logger
import socket
import psutil
import subprocess
# p = [f'pid:{k.pid} status:{k.status} {psutil.Process(k.pid).name()}' for k in psutil.net_connections(kind='all')]
# [k for k in p]

def show_udp():
	result = subprocess.run(["ss", "-unpH4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
	lines = result.stdout.decode("utf-8").split("\n")
	print(f"{len(lines)} UDP sockets:")
	for line in lines:
		if line:
			parts = line.split()
			if len(parts) == 6:
				state = parts[0]
				local_address = parts[3]
				if '%' in local_address:
					local_address = local_address.split('%')[0]
				peer_address = parts[4]
				process_info = parts[5]
				print(f'\tLocal: {local_address} Peer: {peer_address} State: {state} Process: {process_info}')
			elif len(parts) == 5:
				local_interface = ''
				local_port = ''
				state = parts[0]
				local_address = parts[3]
				try:
					if '%' in local_address:
						local_address = local_address.split('%')[0]
						local_interface = parts[3].split('%')[1]
						local_port = parts[3].split(':')[1]
				except IndexError as e:
					logger.error(f'[err] {e} local_address:{local_address} parts:{parts}')
					local_interface = 'N/A'
					local_port = 'N/A'
				peer_address = parts[4]
				print(f'\tLocal: {local_address} interface: {local_interface} port: {local_port} Peer: {peer_address} State: {state} Process: N/A')
			else:
				print(f'\tLine: {line.strip()}')

def show_tcp():
	result = subprocess.run(["ss", "-tnpH4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
	lines = result.stdout.decode("utf-8").split("\n")
	print(f"{len(lines)} TCP sockets:")
	for line in lines:
		if line:
			process_name = ''
			pid = 0
			fd = 0
			parts = line.split()
			if len(parts) == 6:
				state = parts[0]
				local_address = parts[3]
				peer_address = parts[4]
				process_info = parts[5]
				match = re.search(r'\("([^"]+)",pid=(\d+),fd=(\d+)\)', process_info)
			if match:
				process_name = match.group(1)
				pid = int(match.group(2))
				fd = int(match.group(3))
				print(f'\tLocal: {local_address} Peer: {peer_address} State: {state} Process: {process_name} pid:{pid} fd:{fd}')
			else:
				print(f'\tLine: {line.strip()}')

def show_tcp_listen():
	result = subprocess.run(["ss", "-tnpHl4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
	lines = result.stdout.decode("utf-8").split("\n")
	print(f"{len(lines)} Listening TCP sockets:")
	for line in lines:
		process_name = ''
		pid = 0
		fd = 0
		if line:
			parts = line.split()
			if len(parts) == 6:
				state = parts[0]
				local_address = parts[3]
				peer_address = parts[4]
				process_info = parts[5]
				match = re.search(r'\("([^"]+)",pid=(\d+),fd=(\d+)\)', process_info)
			if match:
				process_name = match.group(1)
				pid = int(match.group(2))
				fd = int(match.group(3))

				print(f'\tLocal: {local_address} Peer: {peer_address} State: {state} Process: {process_name} pid:{pid} fd:{fd}')
			else:
				print(f'\tLine: {line.strip()}')

def get_conns():
	conns = psutil.net_connections(kind='inet')
	for k in conns:
		if k.status == 'LISTEN' or k.status == 'ESTABLISHED' or k.status == 'CLOSE_WAIT' or k.status == 'NONE':
			if k.status == 'ESTABLISHED':
				kraddr = k.raddr.ip  # type: ignore
			else:
				kraddr = '-'
			procname = psutil.Process(k.pid).name()
			if k.pid is None:
				kpid = '-'
			else:
				kpid = k.pid
			if k.laddr.ip == '::':  # type: ignore
				kladdrip = '0.0.0.0'
			else:
				kladdrip = k.laddr.ip  # type: ignore
			print(f'l:{kladdrip:<13}:{k.laddr.port:<5} {procname} pid:{kpid} s:{k.status} {kraddr}')  # type: ignore

def get_listeners():
	conn_list = []
	conns = psutil.net_connections(kind='inet4')
	conn_list_temp = sorted(set([(k.laddr.port, k.pid, k.laddr.ip, psutil.Process(k.pid).name()) for k in conns if k.status == 'LISTEN' and isinstance(k.family, type(socket.AF_INET)) ]))  # type: ignore
	for c in conn_list_temp:
		port = c[0]
		ip = c[2]
		process = c[3]
		if c[1] is None:
			pid = '-'
			process = 'N/A'
		else:
			pid = c[1]
		conn_list.append((port, pid, ip, process))
	return conn_list

if __name__ == '__main__':
	listeners = get_listeners()
	print(f'listeners count: {len(listeners)}')
	for k in listeners:
		print(f'\tip:{k[2]:<13} port:{k[0]:<5} pid:{k[1]:<7} process:{k[3]}')
	show_tcp()
	show_tcp_listen()
	show_udp()

