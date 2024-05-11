import os
import sys
import requests
import json
import importlib
import importlib_metadata
import xmlrpc.client
from loguru import logger
import time
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
	time.sleep(0.2) # sleep for 200ms for rate limiting
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
	logger.info(f'total: {len(usrnames) + len(localnames)} / {len(usrpacks)+len(localpacks)} allpacks={len(allpacks)} usr: {len(usrpacks)} local: {len(localpacks)} dupe: {len(dupe_packs)} usrpacklinks: {len(usrpacklinks)} localpacklinks: {len(lockalpacklinks)}')

	usrpackinfojson = [get_pypi_json(k) for k in usrpacklinks ]
	validusrpacks = [k for k in usrpackinfojson if len(k.keys())==5]
	up_errors = [k for k in usrpackinfojson if 'error' in k.keys()]

	localpackjson = [get_pypi_json(k) for k in lockalpacklinks]
	lp_errors = [k for k in localpackjson if 'error' in k.keys()]
	validlocalpackjson = [k for k in localpackjson if len(k.keys())==5]

	logger.info(f'usrpackinfojson: {len(usrpackinfojson)} errors: {len(up_errors)} localpackjson: {len(localpackjson)} errors: {len(lp_errors)}')
	for p in up_errors:
		logger.warning(f'usrpack Error: {p}')
	for p in lp_errors:
		logger.warning(f'localpack Error: {p}')
	logger.info(f'checking usrpacks')
	for pack in usrnames:
		installed_version = get_installed_version(pack)
		latest_version = get_latest_version_cache(pack, usrpackinfojson)
		logger.info(f'Name: {pack} localversion: {installed_version} latestversion: {latest_version}')
	logger.info(f'checking localpacks')
	for pack in localnames:
		installed_version = get_installed_version(pack)
		latest_version = get_latest_version_cache(pack, localpackjson)
		logger.info(f'Name: {pack} localversion: {installed_version} latestversion: {latest_version}')
