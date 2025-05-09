import asyncio
import os
import sys
import argparse
import requests
import json
import importlib
import importlib_metadata
from loguru import logger
import time
from colorama import Fore, Back, Style
from pathlib import Path
import glob


def get_modules():
	usrpacks = []
	localpacks = []
	allpacks = [k for k in set([k for k in importlib_metadata.entry_points()])]
	logger.debug(f'Found {len(allpacks)} modules')
	# cache all module names
	# usrdistmods = [k for k in set( [k.dist.name for k in allpacks if str(k.dist._path).startswith('/usr')])]
	# logger.debug(f'Found {len(usrdistmods)} usrdistmods modules')
	# localdistmods = [k for k in set( [k.dist.name for k in allpacks if str(k.dist._path).startswith('/home')])]
	# logger.debug(f'Found {len(localdistmods)} localdistmods modules')
	usrdistmods = []
	localdistmods = []
	for idx,p in enumerate(allpacks):
		if str(p.dist._path).startswith('/usr') and p.dist.name not in usrdistmods:
			usrpacks.append(p)
			usrdistmods.append(p.dist.name)
		elif str(p.dist._path).startswith('/home/') and p.dist.name not in localdistmods:
			localpacks.append(p)
			localdistmods.append(p.dist.name)
		else:
			pass  # logger.warning(f'[{idx}/{len(allpacks)} {len(usrpacks)}/{len(localpacks)}] unhandled package {p.dist.name} path: {p.dist._path}')
	# usrpacks = [k for k in set([k for k in importlib_metadata.entry_points() if str(k.dist._path).startswith('/usr')])]
	# localpacks = [k for k in set([k for k in importlib_metadata.entry_points() if str(k.dist._path).startswith('/home/')])]
	return allpacks, usrpacks, localpacks

def make_json_link(modulename):
	if '_' in modulename:
		on = modulename
		modulename = modulename.replace('_','-')
		logger.warning(f'fixing modulename {on} to {modulename}')
	info = {'modulename': modulename, 'url': f'https://pypi.org/pypi/{modulename}/json'}
	return info

def get_pypi_json(module):
	url = module['url']
	jsondata = {}
	try:
		r = requests.get(url)
	except Exception as e:
		logger.error(f'Unhandled Exception: {e} {type(e)} {module=} for {url} for module: {module["modulename"]}')
		jsondata = {'error': e, 'url': url, 'module': module['modulename']}
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
	# time.sleep(0.2) # sleep for 200ms for rate limiting
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
	except IndexError as e:
		jsoninfo = [k for k in cachedata if k.get('info').get('name') == packname]
		logger.warning(f'Error: {e} {type(e)} for {packname} jsoninfo:{jsoninfo}')
		latest_version = f'Error {e}'
	except Exception as e:
		logger.error(f'Unhandled Exception: {e} {type(e)} for {packname}')
		latest_version = f'Error {e}'
	if isinstance(jsoninfo, dict):
		if 'info' in jsoninfo.keys():
			if 'version' in jsoninfo.get('info').keys():
				latest_version = jsoninfo.get('info').get('version')
			else:
				latest_version = 'Error: No version in info'
		else:
			latest_version = 'Error: No info in jsoninfo'
	return latest_version

def update_check(allpacks, usrpacks, localpacks):
	usrnames = [k for k in set([k.dist.name for k in usrpacks])]
	localnames = [k for k in set([k.dist.name for k in localpacks])]
	dupe_packs = [k for k in usrpacks if k.dist.name in localnames]
	usrpacklinks = [make_json_link(k) for k in usrnames]
	lockalpacklinks = [make_json_link(k) for k in localnames]
	print(f'{Fore.LIGHTBLUE_EX}total:{Fore.CYAN} {len(usrnames) + len(localnames)} / {len(usrpacks)+len(localpacks)} {Fore.LIGHTBLUE_EX}allpacks={Fore.CYAN}{len(allpacks)} {Fore.LIGHTBLUE_EX}usr:{Fore.CYAN} {len(usrpacks)} {Fore.LIGHTBLUE_EX}local:{Fore.CYAN} {len(localpacks)} {Fore.LIGHTBLUE_EX}dupe:{Fore.CYAN} {len(dupe_packs)} {Fore.LIGHTBLUE_EX}usrpacklinks:{Fore.CYAN} {len(usrpacklinks)} {Fore.LIGHTBLUE_EX}localpacklinks:{Fore.CYAN} {len(lockalpacklinks)}{Style.RESET_ALL}')

	logger.debug(f'loading usrpackinfojson {len(usrpacklinks)}')
	usrpackinfojson = [get_pypi_json(k) for k in usrpacklinks]
	validusrpacks = [k for k in usrpackinfojson if len(k.keys()) == 5]
	up_errors = [k for k in usrpackinfojson if 'error' in k.keys()]

	logger.debug(f'loading validlocalpackjson {len(lockalpacklinks)} upj:{len(usrpackinfojson)} vup:{len(validusrpacks)} ue:{len(up_errors)}')
	localpackjson = [get_pypi_json(k) for k in lockalpacklinks]
	lp_errors = [k for k in localpackjson if 'error' in k.keys()]
	validlocalpackjson = [k for k in localpackjson if len(k.keys()) == 5]

	print(f'{Fore.BLUE}usrpackinfojson: {Fore.CYAN}{len(usrpackinfojson)} {Fore.RED}errors:{Fore.LIGHTRED_EX} {len(up_errors)} {Fore.BLUE} localpackjson: {Fore.CYAN} {len(localpackjson)} {Fore.RED} errors: {Fore.LIGHTRED_EX} {len(lp_errors)} {Style.RESET_ALL}')

	for p in up_errors:
		print(f'{Fore.RED}usrpack Error:{Fore.LIGHTRED_EX} {p}{Style.RESET_ALL}')
	for p in lp_errors:
		print(f'{Fore.RED}localpack Error:{Fore.LIGHTRED_EX} {p}{Style.RESET_ALL}')
	usr_outdated = []
	local_outdated = []
	for pack in usrnames:
		installed_version = get_installed_version(pack)
		try:
			latest_version = get_latest_version_cache(pack, validusrpacks)
		except AttributeError as e:
			logger.error(f'Exception: {e} {type(e)} for {pack}')
			latest_version = 'Error'
		if installed_version != latest_version:
			usr_outdated.append({'pack': pack, 'installed_version': installed_version, 'latest_version': latest_version, 'location': 'usr'})
			print(f'{Fore.BLUE}usrpacks{Fore.CYAN} Name: {pack} localversion: {Fore.RED} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
		else:
			print(f'{Fore.BLUE}usrpacks{Fore.CYAN} Name: {pack} localversion: {Fore.GREEN} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
	print(f'{Fore.RED}usrpacks usr_outdated:{Fore.LIGHTRED_EX} {len(usr_outdated)} {Style.RESET_ALL}')
	for pack in localnames:
		installed_version = get_installed_version(pack)
		try:
			latest_version = get_latest_version_cache(pack, validlocalpackjson)
		except AttributeError as e:
			logger.error(f'Exception: {e} {type(e)} for {pack}')
			latest_version = 'Error'
		if installed_version != latest_version:
			local_outdated.append({'pack': pack, 'installed_version': installed_version, 'latest_version': latest_version, 'location': 'home'})
			print(f'{Fore.BLUE}localpacks{Fore.CYAN} Name: {pack} localversion: {Fore.RED} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
		else:
			print(f'{Fore.BLUE}localpacks{Fore.CYAN} Name: {pack} localversion: {Fore.GREEN} {installed_version} {Fore.BLUE} latestversion: {Fore.LIGHTGREEN_EX} {latest_version}{Style.RESET_ALL}')
	print(f'{Fore.RED}usr_outdated:{Fore.LIGHTRED_EX} {len(usr_outdated)} {Fore.RED}local_outdated:{Fore.LIGHTRED_EX} {len(local_outdated)} {Style.RESET_ALL}')

def check_folders(allpacks, usrpacks, localpacks):
	search_paths = [k for k in sys.path if Path(k).exists() and Path(k).is_dir() and k != '']
	found_folders = []
	for idx,p in enumerate(search_paths):
		print(f'{Fore.LIGHTBLUE_EX}Searching:{Fore.BLUE}{p}{Style.RESET_ALL}')
		for sub_path in Path(p).glob('*'):
			if 'dist-info' in str(sub_path):
				break
			elif sub_path.exists() and sub_path.is_dir():
				found_folders.append(sub_path)
				print(f'{Fore.LIGHTBLUE_EX}[{idx}/{len(search_paths)}] {Fore.CYAN}{sub_path}{Style.RESET_ALL}')

async def main(args):
	allpacks, usrpacks, localpacks = get_modules()
	if args.count:
		print(f'{Fore.LIGHTBLUE_EX}total:{Fore.CYAN} {len(usrpacks)+len(localpacks)} {Fore.LIGHTBLUE_EX}usr:{Fore.CYAN} {len(usrpacks)} {Fore.LIGHTBLUE_EX}local:{Fore.CYAN} {len(localpacks)}{Style.RESET_ALL}')
		sys.exit(0)
	elif args.update:
		print(f'{Fore.LIGHTBLUE_EX}Starting update check{Style.RESET_ALL}')
		try:
			update_check(allpacks, usrpacks, localpacks)
		except Exception as e:
			logger.error(f'unhandled exception: {e} {type(e)}')
		sys.exit(0)
	elif args.check_folders:
		print(f'{Fore.LIGHTBLUE_EX}Checking folders{Style.RESET_ALL}')
		try:
			check_folders(allpacks, usrpacks, localpacks)
		except Exception as e:
			logger.error(f'unhandled exception: {e} {type(e)}')
		sys.exit(0)

if __name__ == '__main__':
	argparser = argparse.ArgumentParser(description='Check installed packages against pypi')
	argparser.add_argument('-v', '--verbose', help='verbose output', action='store_true', default=False, dest='verbose')
	argparser.add_argument('--config',action='store', default='piplist.json', dest='config', type=str, help='config file with module paths to search in')
	argparser.add_argument('--count', action='store_true', default=False, dest='count', help='count installed modules')
	argparser.add_argument('--update-check', action='store_true', default=False, dest='update', help='check for updates')
	argparser.add_argument('--check-folders', action='store_true', default=False, dest='update', help='search for modules in folders (including orphan folders without dist-info)')
	args = argparser.parse_args()
	asyncio.run(main(args))
