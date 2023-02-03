#!/usr/bin/python3

import os, sys
import time
import argparse
from pathlib import Path
import glob
from loguru import logger
from datetime import datetime
import subprocess
from configparser import ConfigParser

def get_folder_list(startpath):
	# foo
	git_folderlist = [Path(k) for k in glob.glob(str(Path(startpath))+'/**',recursive=True, include_hidden=True) if Path(k).is_dir() and Path(k).name == '.git']
	logger.debug(f'[gf] gitfolders {len(git_folderlist)}')
	return git_folderlist

def get_git_remote_config(gitfolder):
	result = None
	conf = ConfigParser()
	base_folder = gitfolder.parent
	git_folder = str(gitfolder)
	git_config_file = f'{git_folder}/config'
	try:
		stat = os.stat(git_config_file)
	except FileNotFoundError as e:
		logger.warning(f'[gconfig] file not found {e} gitfolder={gitfolder} git_config_file={git_config_file}')
		return None
	c = conf.read(git_config_file)
	try:
		giturl = [k for k in conf['remote "origin"'].items()][0][1]
		result = {'gitfolder':gitfolder, 'giturl':giturl }
	except TypeError as e:
		logger.warning(f'[gconfig] typeerror {e} gitfolder={gitfolder} git_config_file={git_config_file} c={c}')
	except KeyError as e:
		logger.warning(f'[gconfig] KeyError {e} gitfolder={gitfolder} git_config_file={git_config_file} c={c}')
	return result

def get_git_remote_cmd(gitfolder):
	os.chdir(gitfolder.parent)
	status = subprocess.run(['git', 'remote', '-v',], capture_output=True)
	if status.stdout != b'':
		remotes = status.stdout.decode('utf-8').split('\n')
		parts = None
		try:
			parts = remotes[0].split('\t')
		except IndexError as e:
			logger.warning(f'[ggr] indexerror {e} {gitfolder}')
			return None
		try:
			if parts:
				origin = parts[0]
				giturl = parts[1].split(' ')[0]
				result = {'gitfolder':gitfolder,'remotes':remotes, 'origin':origin, 'giturl':giturl }
				return result
		except IndexError as e:
			logger.warning(f'[ggr] indexerror {e} git={gitfolder} parts={parts}')
			return {}
	else:
		logger.warning(f'[ggr] no gitremote in {gitfolder} stdout={status.stdout} stderr={status.stderr}')
		return {}


if __name__ == '__main__':
	myparse = argparse.ArgumentParser(description="findgits", exit_on_error=False)
	_default = str(Path(myparse.prog).parent)
	myparse.add_argument('path', nargs='?', type=str, default=_default,	 metavar='input_path')
	args = myparse.parse_args()
	folders = get_folder_list(args.path)
	gitremotes = [get_git_remote_config(k) for k in folders]
	giturls = [k.get('giturl') for k in gitremotes if k]
	unique_giturls = set(giturls)
	logger.info(f'Found {len(giturls)} git repositories unique {len(unique_giturls)}')

