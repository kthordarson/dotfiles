#!/usr/bin/python
from ipwhois import IPWhois
from pprint import pprint
import sys
ipaddr = sys.argv[1]
try:
    ip = ipaddr.strip('\n')
    obj = IPWhois(ip)
    rdap = obj.lookup_rdap()
    # whois =obj.lookup_whois()
    result = "{};{};{};{};{}".format(rdap['asn_description'], rdap['network']['name'] , rdap['network']['cidr'] , rdap['network']['start_address'] , rdap['network']['end_address'])
    print (result)
except:
    pass


