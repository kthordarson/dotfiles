#!/usr/bin/python3
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
			if len(parts) >= 6:
				state = parts[0]
				local_address = parts[3]
				peer_address = parts[4]
				process_info = parts[5]
				print(f'\tLocal: {local_address} Peer: {peer_address} State: {state} Process: {process_info}')
			else:
				print(f'\tLine: {line.strip()}')

def show_tcp():
	result = subprocess.run(["ss", "-tnpH4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
	lines = result.stdout.decode("utf-8").split("\n")
	print(f"{len(lines)} TCP sockets:")
	for line in lines:
		if line:
			parts = line.split()
			if len(parts) >= 6:
				state = parts[0]
				local_address = parts[3]
				peer_address = parts[4]
				process_info = parts[5]
				print(f'\tLocal: {local_address} Peer: {peer_address} State: {state} Process: {process_info}')
			else:
				print(f'\tLine: {line.strip()}')

def show_tcp_listen():
	result = subprocess.run(["ss", "-tnpHl4"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
	lines = result.stdout.decode("utf-8").split("\n")
	print(f"{len(lines)} Listening TCP sockets:")
	for line in lines:
		if line:
			parts = line.split()
			if len(parts) >= 6:
				state = parts[0]
				local_address = parts[3]
				peer_address = parts[4]
				process_info = parts[5]
				print(f'\tLocal: {local_address} Peer: {peer_address} State: {state} Process: {process_info}')
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
	conns = psutil.net_connections(kind='inet')
	return sorted(set([(k.laddr.port, k.pid, k.laddr.ip, psutil.Process(k.pid).name()) for k in conns if k.status == 'LISTEN' and isinstance(k.family, type(socket.AF_INET))]))  # type: ignore

if __name__ == '__main__':
	listeners = get_listeners()
	print(f'listeners count: {len(listeners)}')
	for k in listeners:
		print(f'\t{k}')
	show_tcp()
	show_tcp_listen()
	show_udp()

