#!/usr/bin/env python3
import os
import sys
import pathlib
import glob
import re

def process_file(procnet):
	sockets = procnet.split('\n')[1:-1]
	return [line.strip() for line in sockets]

def split_every_n(data, n):
	return [data[i:i+n] for i in range(0, len(data), n)]

def convert_linux_netaddr(address):

	hex_addr, hex_port = address.split(':')

	addr_list = split_every_n(hex_addr, 2)
	addr_list.reverse()

	addr = ".".join(map(lambda x: str(int(x, 16)), addr_list))
	port = str(int(hex_port, 16))

	return "{}:{}".format(addr, port)

def format_line(data):
	return (("%(seq)-4s %(uid)5s %(local)25s %(remote)25s %(timeout)8s %(inode)8s" % data) + "\n")

def readnet(pid) -> list:
	with open(f'/proc/{pid}/net/tcp') as f:
		sockets = process_file(f.read())
	columns = ("seq", "uid", "inode", "local", "remote", "timeout")
	title = dict()
	for c in columns:
		title[c] = c
	rv = []
	for info in sockets:
		_ = re.split(r'\s+', info)
		_tmp = {
			'seq': _[0],
			'local': convert_linux_netaddr(_[1]),
			'remote': convert_linux_netaddr(_[2]),
			'uid': _[7],
			'timeout': _[8],
			'inode': _[9],
		}
		rv.append(_tmp)
	return rv

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: python findopenfiles.py <pid>")
		sys.exit(1)
	search_string = sys.argv[1]
	results = {}
	for pid in glob.glob('/proc/*/fd/*'):
		pid = pathlib.Path(pid).parts[2]
		if pid not in results:
			results[pid] = {
				'symlinks': [],
				'files': [],
				'dirs': [],
				'sockets': [],
				'pipes': [],
				'other': []
			}

	for k in glob.glob('/proc/*/fd/*'):
		if pathlib.Path(k).exists():
			p = pathlib.Path(k)
			rl = p.readlink()
			pid = p.parts[2]
			if search_string in str(p) or search_string in str(rl):
				print(f"{search_string} Found: {p} -> {rl} (pid: {pid})")
			if rl.is_symlink():
				results[pid]['symlinks'].append(rl)
			elif rl.is_file():
				results[pid]['files'].append(rl)
			elif rl.is_dir():
				results[pid]['dirs'].append(rl)
			elif rl.is_socket() or p.is_socket():
				results[pid]['sockets'].append(rl)
				connections = readnet(pid)
				results[pid]['connections'] = connections
				# if search_string in ' '.join([f"{c['local']} -> {c['remote']}" for c in connections]):
				# 	print(f"{search_string} Found in connections: {len(connections)} (pid: {pid})")
			elif rl.is_fifo():
				results[pid]['pipes'].append(rl)
			else:
				results[pid]['other'].append(rl)



