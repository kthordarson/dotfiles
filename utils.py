import os
import fnmatch
from pathlib import Path
from loguru import logger
from dataclasses import dataclass, field

EXCLUDES = ['.git', '__pycache__', '.idea', '.vscode', '.ipynb_checkpoints']

@dataclass(order=True, frozen=False)
class FileItem:
	sort_index: int = field(init=False, repr=False)
	name: Path
	size: int = 0
	st_atime: float = 0.0
	st_mtime: float = 0.0
	st_ctime: float = 0.0

	def __init__(self, name:Path):
		object.__setattr__(self, 'sort_index', self.size)
		self.name = Path(name)
		self.filename = str(name)
		try:
			self.size = self.name.stat().st_size
		except AttributeError as e:
			logger.error(f'[err] {e} file: {self.filename}')
		except FileNotFoundError as e:
			logger.warning(f'[err] {e} file: {self.filename}')
			return
		self.st_atime = self.name.stat().st_atime
		self.st_mtime = self.name.stat().st_mtime
		self.st_ctime = self.name.stat().st_ctime

	def __post_init__(self):
		# Set sort_index to size for proper ordering
		object.__setattr__(self, 'sort_index', self.size)

	def __str__(self):
		return f'{self.name}'

	def get_size(self):
		return get_size_format(self.size,suffix='B')

def get_size_format(b, factor=1024, suffix="B"):
	for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
		if b < factor:
			return f"{b:.2f} {unit}{suffix}"
		b /= factor
	return f"{b:.2f} {suffix}"

# This would go in your utils.py file
def filelist_generator(args, exclude_list, specific_dir=None, root_only=False):
	path = specific_dir or Path(args.path)
	wildcard = args.wildcard

	# Use scandir instead of Path.glob for better performance
	if root_only:
		for entry in os.scandir(path):
			if entry.is_file() and not entry.name.startswith('.') and entry.name not in exclude_list:
				if fnmatch.fnmatch(entry.name, wildcard):
					stat = entry.stat()
					yield FileItem(name=Path(entry.path))
	else:
		for root, dirs, files in os.walk(path):
			# Skip excluded directories
			dirs[:] = [d for d in dirs if d not in exclude_list]

			for file in files:
				if file not in exclude_list and fnmatch.fnmatch(file, wildcard):
					full_path = os.path.join(root, file)
					try:
						size = os.path.getsize(full_path)
						yield FileItem(name=Path(full_path))
					except (FileNotFoundError, PermissionError):
						continue

def xfilelist_generator(args, excludes):
	startpath = Path(args.path)
	filelist_ = [k for k in startpath.rglob(f'{args.wildcard}')]
	logger.debug(f'[flg] :{len(filelist_)}')
	for file in filelist_:
		try:
			if Path(file).is_file() and len([p for p in file.parts if p in excludes]) == 0:
				yield (FileItem(file))
				# yield((Path(file), Path(file).stat().st_size, Path(file).stat().st_ctime))
		except PermissionError as e:
			logger.warning(f'[err] {e} file: {file}')
		except TypeError as e:
			logger.error(f'[err] {e} file: {file}')

@dataclass(order=True, frozen=False)
class FileItemx:
	sort_index: int = field(init=False, repr=False)
	name: Path
	size: int = 0

	def __init__(self, name:Path):
		self.name = name
		self.filename = str(name.name)
		self.size = self.name.stat().st_size

	def __str__(self):
		return f'{self.name}'

	def get_size(self):
		return get_size_format(self.size,suffix='B')

@dataclass(order=True, frozen=False)
class DirItem:
	sort_index: int = field(init=False, repr=False)
	name: Path
	totalsize: int = 0
	subfilecount: int = 0
	subdircount: int = 0
	subitemcount: int = 0
	# bigfiles: list = []

	def __init__(self, name:Path, getbigfiles=False, maxfiles=3, wildcard='*'):
		self.name = name
		self.dirname = str(name.name)
		self.maxfiles = maxfiles
		self.wildcard = wildcard
		self.totalsize = get_directory_size(self.name, self.wildcard)
		self.subfilecount = get_subfilecount(self.name)
		self.subdircount = get_subdircount(self.name)
		self.subitemcount = self.subfilecount + self.subdircount
		self.bigfiles = []
		self.filelist = []
		if getbigfiles:
			self.get_bigfiles()

	def __post_init(self):
		object.__setattr__(self, 'sort_index', self.totalsize)

	def __str__(self):
		return f'{self.name}'

	def __repr__(self) -> str:
		return f'{self.name}'

	def get_size(self):
		return get_size_format(self.totalsize,suffix='B')

	def get_bigfiles(self):
		subfiles = [FileItem(k) for k in self.name.glob(f'**/{self.wildcard}') if k.is_file()]
		self.bigfiles = sorted(subfiles, key=lambda d: d.size, reverse=True)[0:self.maxfiles]


def get_directory_size(directory, wildcard='*'):
	total = 0
	entry = None
	try:
		for entry in os.scandir(directory):
			try:
				if Path(entry).is_symlink():
					# if Path(entry).is_file():
					# print(f'[!] {entry.name} is symlink to {Path(entry).resolve()}')
					continue
				if entry.is_file() and Path(entry).match(wildcard):
					total += entry.stat().st_size
				elif entry.is_dir():
					try:
						total += get_directory_size(entry.path, wildcard)
					except FileNotFoundError as e:
						logger.error(f'[err] {e} entry:{entry}')
						continue
			except OSError as e:
				logger.warning(f'[err]  {entry} {e}')
				return total
			# return os.path.getsize(directory)
	except NotADirectoryError as e:
		logger.error(f'[err] dir:{directory} {e}')
		return os.path.getsize(directory)
	except (PermissionError, FileNotFoundError) as e:
		logger.error(f'[err] dir:{directory} {e}')
		return 0
	return total

def get_subfilecount(directory):
	try:
		filecount = len([k for k in directory.glob('**/*') if k.is_file()])
	except PermissionError as e:
		logger.error(f'[err] {e} d:{directory}')
		return 0
	return filecount

def get_subdircount(directory):
	dc = 0
	try:
		dc = len([k for k in directory.glob('**/*') if k.is_dir()])
	except (PermissionError,FileNotFoundError) as e:
		logger.error(f'[err] {e} d:{directory}')
	return dc

def format_bytes(size):
	# 2**10 = 1024
	power = 2**10
	n = 0
	power_labels = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
	while size > power:
		size /= power
		n += 1
	return size, power_labels[n]+'bytes'

def humanbytes(bytesinput):
	"""Return the given bytes as a human friendly KB, MB, GB, or TB string."""
	bytesinput = float(bytesinput)
	kilobytes = float(1024)
	megabytes = float(kilobytes ** 2)  # 1,048,576
	gigabytes = float(kilobytes ** 3)  # 1,073,741,824
	terabytes = float(kilobytes ** 4)  # 1,099,511,627,776

	if bytesinput < kilobytes:
		return f'{bytesinput:.0f} B'  # return f'{0} {1}'.format(B,'B' if 0 == B > 1 else 'B')
	elif kilobytes <= bytesinput < megabytes:
		return '{0:.0f} KB'.format(bytesinput / kilobytes)
	elif megabytes <= bytesinput < gigabytes:
		return '{0:.0f} MB'.format(bytesinput / megabytes)
	elif gigabytes <= bytesinput < terabytes:
		return '{0:.0f} GB'.format(bytesinput / gigabytes)
	elif terabytes <= bytesinput:
		return '{0:.0f} TB'.format(bytesinput / terabytes)
