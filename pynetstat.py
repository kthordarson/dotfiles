#!/usr/bin/python3

import socket
from socket import AF_INET
from socket import SOCK_DGRAM
from socket import SOCK_STREAM

import psutil

AD = "-"
AF_INET6 = getattr(socket, 'AF_INET6', object())
proto_map = {
    (AF_INET, SOCK_STREAM): 'tcp',
    (AF_INET6, SOCK_STREAM): 'tcp6',
    (AF_INET, SOCK_DGRAM): 'udp',
    (AF_INET6, SOCK_DGRAM): 'udp6',
}

def get_res():
    # templ = "%-5s %-30s %-30s %-13s %-6s %s"
    # print(templ % ("Proto", "Local address", "Remote address", "Status", "PID", "Program name"))
    proc_names = {}
    res = []
    for p in psutil.process_iter(['pid', 'name']):
        proc_names[p.info['pid']] = p.info['name']
    for c in psutil.net_connections(kind='inet'):
        laddr = "%s:%s" % (c.laddr)
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % (c.raddr)
        name = proc_names.get(c.pid, '?') or ''
        # print(templ % (proto_map[(c.family, c.type)], laddr, raddr or AD, c.status, c.pid or AD, name[:15],))
        item = {'proto': proto_map[(c.family, c.type)], 'laddr': laddr, 'raddr': raddr or AD, 'status': c.status, 'pid': c.pid or AD, 'name': name[:15]}
        res.append(item)
    return res

if __name__ == '__main__':
    res = get_res()
    listeners = [k for k in res if k['status'] == 'LISTEN']
    established = [k for k in res if k['status'] == 'ESTABLISHED']
    if established:
        print("Established connections:")
        for k in established:
            print(f"\tproto: {k['proto']} addr: {k['laddr']} raddr: {k['raddr']} pid: {k['pid']} {k['name']}")
    else:
        print("No established connections found.")
    if listeners:
        print("Listening ports:")
        for k in listeners:
            print(f"\tproto: {k['proto']} addr: {k['laddr']} pid: {k['pid']} {k['name']}")
    else:
        print("No listening ports found.")
    print("All connections:")
    for k in res:
        print(f"\tproto: {k['proto']} addr: {k['laddr']} raddr: {k['raddr']} pid: {k['pid']} {k['name']} {k['status']}")