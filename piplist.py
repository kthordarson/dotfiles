import os
import sys
import requests
import json
import importlib
import importlib_metadata
import xmlrpc.client
from loguru import logger
import time
from colorama import Fore, Back, Style

def get_modules():
	allpacks = [k for k in set([k for k in importlib_metadata.entry_points() ])]
	usrpacks = [k for k in set([k for k in importlib_metadata.entry_points() if str(k.dist._path).startswith('/usr')])]
	localpacks = [k for k in set([k for k in importlib_metadata.entry_points() if str(k.dist._path).startswith('/home/')])]
	return allpacks, usrpacks, localpacks

def make_json_link(modulename):
	info = {'modulename': modulename, 'url': f'https://pypi.org/pypi/{modulename}/json'}
	return info

def get_pypi_json(module):
	url = module['url']
	jsondata = {}
	try:
		r = requests.get(url)
	except Exception as e:
		logger.error(f'Unhandled Exception: {e} {type(e)} {module=} for {url} for module: {module["modulename"]}')
		jsondata = {'error': e, 'status_code': r.status_code, 'url': url, 'module': module['modulename']}
		# Error: <Fault -32500: 'HTTPTooManyRequests: The action could not be performed because there were too many requests by the client.'> <class 'xmlrpc.client.Fault'> https://pypi.org/pypi/pyroute2.ipdb/json
	if r.status_code == 200:
		try:
			jsondata = r.json()
		except Exception as e:
			logger.error(f'Unhandled Exception: {e} {type(e)} for {url} response: {r.status_code}')
			jsondata = {'error': e, 'status_code': r.status_code, 'url': url, 'module': module['modulename']}
	elif r.status_code == 404:
		logger.warning(f'modulenotfound {module["modulename"]} {url=} response: {r.status_code} ')
		jsondata = {'error': '404 Not Found','url': url, 'module': module['modulename']}
	else:
		logger.error(f'moduleerror {module["modulename"]} {url} response: {r.status_code}')
		jsondata = {'error': f'{r.status_code} Error','url': url, 'module': module['modulename']}
	#time.sleep(0.2) # sleep for 200ms for rate limiting
	return jsondata

def get_installed_version(packname):
	try:
		installed_version = importlib_metadata.version(packname)
	except Exception as e:
		logger.error(f'Unhandled Exception: {e} {type(e)} for {packname}')
		installed_version = 'Error'
	return installed_version

def get_latest_version_online(packname):
	latest_version = '0.0.0'
	try:
		jsoninfo = get_pypi_json(make_json_link(packname))
	except Exception as e:
		logger.error(f'Unhandled Exception: {e} {type(e)} for {packname}')
		latest_version = f'Error {e}'
	if 'info' in jsoninfo.keys():
		if 'version' in jsoninfo.get('info').keys():
			latest_version = jsoninfo.get('info').get('version')
		else:
			latest_version = 'Error: No version in info'
	else:
		latest_version = 'Error: No info in jsoninfo'
	return latest_version

def get_latest_version_cache(packname, cachedata):
	latest_version = '0.0.0'
	jsoninfo = {}
	try:
		jsoninfo = [k for k in cachedata if k.get('info').get('name') == packname][0]
	except Exception as e:
		logger.error(f'Unhandled Exception: {e} {type(e)} for {packname}')
		latest_version = f'Error {e}'
	if 'info' in jsoninfo.keys():
		if 'version' in jsoninfo.get('info').keys():
			latest_version = jsoninfo.get('info').get('version')
		else:
			latest_version = 'Error: No version in info'
	else:
		latest_version = 'Error: No info in jsoninfo'
	return latest_version

if __name__ == '__main__':
	client = xmlrpc.client.ServerProxy('https://pypi.org/pypi')
	#client.package_releases('roundup')
	allpacks, usrpacks, localpacks = get_modules()
	all_installed_names = [k for k in set(k.dist.name for k in allpacks)]
	usrnames = [k for k in set([k.dist.name for k in usrpacks])]
	localnames = [k for k in set([k.dist.name for k in localpacks])]
	dupe_packs = [k for k in usrpacks if k.dist.name in localnames]
	usrpacklinks = [make_json_link(k) for k in usrnames]
	lockalpacklinks = [make_json_link(k) for k in localnames]
	print(f'{Fore.LIGHTBLUE_EX}total:{Fore.CYAN} {len(usrnames) + len(localnames)} / {len(usrpacks)+len(localpacks)} {Fore.LIGHTBLUE_EX}allpacks={Fore.CYAN}{len(allpacks)} {Fore.LIGHTBLUE_EX}usr:{Fore.CYAN} {len(usrpacks)} {Fore.LIGHTBLUE_EX}local:{Fore.CYAN} {len(localpacks)} {Fore.LIGHTBLUE_EX}dupe:{Fore.CYAN} {len(dupe_packs)} {Fore.LIGHTBLUE_EX}usrpacklinks:{Fore.CYAN} {len(usrpacklinks)} {Fore.LIGHTBLUE_EX}localpacklinks:{Fore.CYAN} {len(lockalpacklinks)}{Style.RESET_ALL}')
	usrpackinfojson = [get_pypi_json(k) for k in usrpacklinks ]
	validusrpacks = [k for k in usrpackinfojson if len(k.keys())==5]
	up_errors = [k for k in usrpackinfojson if 'error' in k.keys()]

	localpackjson = [get_pypi_json(k) for k in lockalpacklinks]
	lp_errors = [k for k in localpackjson if 'error' in k.keys()]
	validlocalpackjson = [k for k in localpackjson if len(k.keys())==5]

	print(f'{Fore.BLUE}usrpackinfojson: {Fore.CYAN}{len(usrpackinfojson)} {Fore.RED}errors:{Fore.LIGHTRED_EX} {len(up_errors)} {Fore.BLUE} localpackjson: {Fore.CYAN} {len(localpackjson)} {Fore.RED}errors: {Fore.LIGHTRED_EX} {len(lp_errors)} {Style.RESET_ALL}')
	for p in up_errors:
		print(f'{Fore.RED} usrpack Error:{Fore.LIGHTRED_EX} {p}{Style.RESET_ALL}')
	for p in lp_errors:
		print(f'{Fore.RED}localpack Error:{Fore.LIGHTRED_EX} {p}{Style.RESET_ALL}')
	for pack in usrnames:
		installed_version = get_installed_version(pack)
		latest_version = get_latest_version_cache(pack, validusrpacks)
		if installed_version != latest_version:
			print(f'{Fore.BLUE}usrpacks{Fore.CYAN} Name: {pack} localversion: {Fore.RED} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
		else:
			print(f'{Fore.BLUE}usrpacks{Fore.CYAN} Name: {pack} localversion: {Fore.GREEN} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
	for pack in localnames:
		installed_version = get_installed_version(pack)
		latest_version = get_latest_version_cache(pack, validlocalpackjson)
		if installed_version != latest_version:
			print(f'{Fore.BLUE}localpacks{Fore.CYAN} Name: {pack} localversion: {Fore.RED} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
		else:
			print(f'{Fore.BLUE}localpacks{Fore.CYAN} Name: {pack} localversion: {Fore.GREEN} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
