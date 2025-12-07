import os
import aiohttp
import asyncio
from loguru import logger
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup

CACHE_DIR = os.path.join(os.path.expanduser('~'), '.cache', 'gitstars')

async def get_git_stars_async(auth, max=None):
	"""Get all starred repos asynchronously"""
	jsonbuffer = []
	stars_dict = {}
	apiurl = 'https://api.github.com/user/starred'
	headers = {
		'Accept': 'application/vnd.github+json',
		'Authorization': f'Bearer {auth.password}',
		'X-GitHub-Api-Version': '2022-11-28'
	}

	async with aiohttp.ClientSession(headers=headers) as session:
		# Get first page to find total pages
		async with session.get(apiurl) as r:
			if r.status != 200:
				logger.error(f"[r] {r.status}")
				return [], {}

			data = await r.json()
			jsonbuffer.extend(data)
			for s in data:
				stars_dict[s['id']] = s

			if 'link' not in r.headers:
				return jsonbuffer, stars_dict

			# Parse last page number
			links = r.headers['link'].split(',')
			lasturl = [k for k in links if 'last' in k][0].split('>')[0].replace('<', '')
			last_page = int(lasturl.split('=')[-1])

		# Fetch remaining pages concurrently
		max_page = min(last_page, max) if max else last_page
		tasks = [session.get(f"{apiurl}?page={p}") for p in range(2, max_page + 1)]
		logger.debug(f"[r] tasks: {len(tasks)} pages to fetch")
		responses = await asyncio.gather(*tasks)
		logger.debug(f"[r] fetched {len(responses)} pages")
		for resp in responses:
			if resp.status == 200:
				data = await resp.json()
				jsonbuffer.extend(data)
				for s in data:
					stars_dict[s['id']] = s

	return jsonbuffer, stars_dict

def get_git_stars(auth, max=None, use_cache=False):
	"""
	get all starred repos
	param auth: HTTPBasicAuth
	"""
	# tmpfn = 'starred.tmp'
	jsonbuffer = []
	star_list = []
	stars_dict = {}
	session = requests.session()
	apiurl = 'https://api.github.com/user/starred?per_page=100'
	headers = {
		'Accept': 'application/vnd.github+json',
		'Authorization': f'Bearer {auth.password}',
		'X-GitHub-Api-Version': '2022-11-28'}
	try:
		r = session.get(apiurl, headers=headers)
	except Exception as e:
		logger.error(f"[r] {e}")
		return []
	logger.info(f"[r] {r.status_code}  ")
	if r.status_code == 401:
		logger.error(f"[r] autherr:401 a:{auth}")
	elif r.status_code == 404:
		logger.warning(f"[r] {r.status_code} {apiurl} not found")
	elif r.status_code == 403:
		logger.warning(f"[r] {r.status_code} {apiurl} API rate limit exceeded")
	elif r.status_code == 200:
		jsonbuffer.extend(r.json())
		for s in r.json():
			stars_dict[s['id']] = s
		logger.debug(f"[r] page:1 jsonbuffer: {len(jsonbuffer)} stars_dict: {len(stars_dict)}")
	if 'link' in r.headers:
		page_count = 0
		links = r.headers['link'].split(',')
		nexturl = [k for k in links if 'next' in k][0].split('>')[0].replace('<','')
		lasturl = [k for k in links if 'last' in k][0].split('>')[0].replace('<','')
		last_page_no = lasturl.split('=')[1]
		while 'link' in r.headers:
			if max and page_count >= max:
				logger.warning(f'[r] p:{page_count}/{last_page_no} nexturl: {nexturl} hit max: {max}')
				break
			logger.debug(f'[r] p:{page_count}/{last_page_no} nexturl: {nexturl}')
			r = session.get(nexturl, headers=headers)
			if r.status_code == 200:
				jsonbuffer.extend(r.json())
				for s in r.json():
					stars_dict[s['id']] = s
				page_count += 1
				if 'link' in r.headers:
					links = r.headers['link'].split(',')
					if links:
						try:
							nexturl = [k for k in links if 'next' in k][0].split('>')[0].replace('<','')
						except IndexError as e:
							logger.error(f"[r] {e} links: {links} no next link found")
							break
				else:
					logger.warning(f'[r] {r.status_code} link not in headers: {r.headers} nexturl: {nexturl}')
					break
			else:
				logger.warning(f'[r] {r.status_code} {nexturl}')
				break
	else:
		logger.warning(f'[r] {r.status_code} link not in headers: {r.headers} ')
	logger.info(f"[r] {r.status_code}  apiurl: {apiurl} jsonbuffer: {len(jsonbuffer)} stars_dict: {len(stars_dict)}")
	return jsonbuffer, stars_dict

def get_git_lists(auth:HTTPBasicAuth, use_cache=False) -> dict:
	"""
	get lists of starred repos
	param auth: HTTPBasicAuth
	returns dict of lists
	"""
	# todo handle pagination better ....
	# todo handle cache better
	listurl = f'https://github.com/{auth.username}?tab=stars'
	headers = {'Authorization': f'Bearer {auth.password}','X-GitHub-Api-Version': '2022-11-28'}
	session = requests.session()
	session.headers.update(headers)
	soup = None
	if use_cache:
		try:
			with open('starlist.tmp', 'r') as f:
				soup = BeautifulSoup(f.read(), 'html.parser')
		except Exception as e:
			logger.error(f'failed to read starlist.tmp {e}')
	if not soup:
		r = session.get(listurl)
		soup = BeautifulSoup(r.text, 'html.parser')
		with open('starlist.tmp', 'w') as f:
			f.write(str(soup))
	listsoup = soup.find_all('div', attrs={"id": "profile-lists-container"})
	list_items = listsoup[0].find_all('a', attrs={'class':'d-block Box-row Box-row--hover-gray mt-0 color-fg-default no-underline'})  # type: ignore
	logger.debug(f'list_items: {len(list_items)} listsoup: {len(listsoup)}')
	lists = {}
	for item in list_items:
		listname = item.find('h3').text  # type: ignore
		list_link = f"https://github.com{item.attrs['href']}"  # type: ignore
		list_count_info = item.find('div', class_="color-fg-muted text-small no-wrap").text  # type: ignore
		logger.debug(f'listname: {listname} list_link: {list_link} list_count_info: {list_count_info}')
		try:
			list_description = item.select('span', class_="Truncate-text color-fg-muted mr-3")[1].text.strip()  # type: ignore
		except IndexError as e:
			# logger.warning(f'{e} no description for {listname}')
			list_description = ''
		try:
			list_repos = get_info_for_list(list_link, session, use_cache)
		except Exception as e:
			logger.warning(f'{e} {type(e)} failed to get list info for {listname}')
			list_repos = []
		lists[listname] = {'href': list_link, 'count': list_count_info, 'description': list_description, 'hrefs': list_repos}
	return lists

def get_info_for_list(link, session, use_cache):
	"""
	get info for a list
	param list_href: str
	param auth: HTTPBasicAuth
	"""
	# todo handle pagination
	# todo maybe pull more info here
	# todo handle cache better
	link_fn = CACHE_DIR + '/' + link.split('/')[-1] + '.tmp'
	soup = None
	if use_cache:
		try:
			with open(link_fn, 'r') as f:
				soup = BeautifulSoup(f.read(), 'html.parser')
		except FileNotFoundError as e:
			pass  # logger.warning(f'failed to read {link_fn} {e}')
		except Exception as e:
			logger.error(f'failed to read {link_fn} {e}')
	if not soup:
		r = session.get(link)
		soup = BeautifulSoup(r.content, 'html.parser')
	# soup = BeautifulSoup(r.read(), "html.parser")
	try:
		with open(link_fn, 'w') as f:
			f.write(str(soup))
	except Exception as e:
		logger.error(f'failed to write {link_fn} {e} {type(e)}')
	# userlist_repos_data = soup.select_one('div', attrs={"id":"user-list-repositories"})
	# userlist_repos_data = soup.find('div', attrs={"id":"user-list-repositories", "class":"border-top mt-5"})
	# len(soup.select_one('div', attrs={"id":"user-list-repositories","class":"my-3"}))
	soupdata = soup.select_one('div', attrs={"id":"user-list-repositories","class":"my-3"})
	listdata = soupdata.find_all('div', class_="col-12 d-block width-full py-4 border-bottom color-border-muted")
	list_hrefs = [k.find('div', class_='d-inline-block mb-1').find('a').attrs['href'] for k in listdata]  # type: ignore
	logger.debug(f'list_hrefs: {len(list_hrefs)} for {link}')  # type: ignore
	return list_hrefs

def get_updated_at_sort(x) -> HTTPBasicAuth:
	return x['updated_at']

def get_auth_param():
	try:
		auth = HTTPBasicAuth(os.getenv("GITHUB_USERNAME",''), os.getenv("GITSTARSTOKEN",''))
	except Exception as e:
		logger.error(f'failed to get auth param {e} {type(e)}')
		exit(1)
	return auth

async def get_info_for_list_async(link, session: aiohttp.ClientSession, use_cache=False):
	"""
	get info for a list asynchronously with pagination support
	param link: str
	param session: aiohttp.ClientSession
	param use_cache: bool
	"""
	link_fn = CACHE_DIR + '/' + link.split('/')[-1] + '.tmp'
	list_hrefs = []
	page = 1
	max_pages = 50  # Safety limit to prevent infinite loops

	while page <= max_pages:
		page_link = f"{link}?page={page}" if page > 1 else link
		cache_fn = f"{link_fn}.page{page}" if page > 1 else link_fn
		soup = None

		if use_cache:
			try:
				with open(cache_fn, 'r') as f:
					soup = BeautifulSoup(f.read(), 'html.parser')
			except FileNotFoundError:
				pass
			except Exception as e:
				logger.error(f'failed to read {cache_fn} {e}')

		if not soup:
			async with session.get(page_link) as r:
				content = await r.text()
				soup = BeautifulSoup(content, 'html.parser')
				logger.debug(f'fetched list page: {page_link} status: {r.status}')

		try:
			with open(cache_fn, 'w') as f:
				f.write(str(soup))
		except Exception as e:
			logger.error(f'failed to write {cache_fn} {e} {type(e)}')

		soupdata = soup.select_one('div', attrs={"id": "user-list-repositories", "class": "my-3"})
		if not soupdata:
			logger.warning(f'no more data on page {page} for {link}')
			break

		listdata = soupdata.find_all('div', class_="col-12 d-block width-full py-4 border-bottom color-border-muted")
		if not listdata:
			logger.warning(f'no list items on page {page} for {link}')
			break

		page_hrefs = [k.find('div', class_='d-inline-block mb-1').find('a').attrs['href'] for k in listdata]  # type: ignore
		list_hrefs.extend(page_hrefs)
		logger.debug(f'page {page}: found {len(page_hrefs)} repos, total: {len(list_hrefs)} for {link}')

		# Check for next page - multiple ways GitHub shows pagination
		has_next = False

		# Method 1: Look for pagination container with next link
		pagination = soup.find('div', class_='paginate-container')
		if pagination:
			next_link = pagination.find('a', string='Next')  # type: ignore
			if not next_link:
				next_link = pagination.find('a', class_='next_page')  # type: ignore
			if next_link and 'disabled' not in next_link.get('class', []):  # type: ignore
				has_next = True

		# Method 2: Look for BtnGroup pagination
		if not has_next:
			btn_group = soup.find('div', class_='BtnGroup')
			if btn_group:
				next_btn = btn_group.find('a', string='Next')  # type: ignore
				if next_btn and 'disabled' not in next_btn.get('class', []):  # type: ignore
					has_next = True

		# Method 3: Check if we got a full page (30 items = likely more pages)
		if not has_next and len(page_hrefs) == 30:
			has_next = True
			logger.info(f'page {page} has 30 items, assuming more pages exist')

		if not has_next:
			logger.warning(f'no next page found after page {page} for {link}')
			break

		page += 1

	logger.info(f'total list_hrefs: {len(list_hrefs)} from {page} pages for {link}')
	return list_hrefs

async def get_git_lists_async(auth: HTTPBasicAuth, use_cache=False) -> dict:
	"""
	get lists of starred repos asynchronously
	param auth: HTTPBasicAuth
	returns dict of lists
	"""
	listurl = f'https://github.com/{auth.username}?tab=stars'
	headers = {'Authorization': f'Bearer {auth.password}', 'X-GitHub-Api-Version': '2022-11-28'}
	soup = None

	if use_cache:
		try:
			with open('starlist.tmp', 'r') as f:
				soup = BeautifulSoup(f.read(), 'html.parser')
		except Exception as e:
			logger.error(f'failed to read starlist.tmp {e}')

	async with aiohttp.ClientSession(headers=headers) as session:
		if not soup:
			async with session.get(listurl) as r:
				text = await r.text()
				soup = BeautifulSoup(text, 'html.parser')
				with open('starlist.tmp', 'w') as f:
					f.write(str(soup))

		listsoup = soup.find_all('div', attrs={"id": "profile-lists-container"})
		list_items = listsoup[0].find_all('a', attrs={'class': 'd-block Box-row Box-row--hover-gray mt-0 color-fg-default no-underline'})  # type: ignore
		logger.debug(f'list_items: {len(list_items)} listsoup: {len(listsoup)}')

		# Prepare list metadata
		list_meta = []
		for item in list_items:
			listname = item.find('h3').text  # type: ignore
			list_link = f"https://github.com{item.attrs['href']}"  # type: ignore
			list_count_info = item.find('div', class_="color-fg-muted text-small no-wrap").text  # type: ignore
			try:
				list_description = item.select('span', class_="Truncate-text color-fg-muted mr-3")[1].text.strip()  # type: ignore
			except IndexError:
				list_description = ''
			list_meta.append((listname, list_link, list_count_info, list_description))

		# Fetch all list repos concurrently
		tasks = [get_info_for_list_async(meta[1], session, use_cache) for meta in list_meta]
		results = await asyncio.gather(*tasks, return_exceptions=True)

		lists = {}
		for (listname, list_link, list_count_info, list_description), result in zip(list_meta, results):
			if isinstance(result, Exception):
				logger.warning(f'{result} {type(result)} failed to get list info for {listname}')
				list_repos = []
			else:
				list_repos = result
			lists[listname] = {'href': list_link, 'count': list_count_info, 'description': list_description, 'hrefs': list_repos}

	return lists

async def main():
	if not os.path.exists(CACHE_DIR):
		logger.debug(f'creating cache dir: {CACHE_DIR}')
		os.makedirs(CACHE_DIR)
	use_cache = False
	auth = get_auth_param()
	lists = await get_git_lists_async(auth, use_cache)
	logger.info(f'got {len(lists)} lists')
	# starred_repos, stars_dict = await get_git_stars_async(auth=auth)
	# # sorted(starred_repos,key=get_updated_at_sort,reverse=True)
	# idlist = [k['id'] for k in starred_repos]
	# logger.debug(f'idlist: {len(idlist)} lists: {len(lists)} stars: {len(starred_repos)}')
	# _ = [print(f'id: {k['id']} {k['name']} {k['updated_at']}') for k in starred_repos]
	# _ = [print(k.get('name')  in ''.join([''.join(lists[k].get('hrefs')) for k in lists]))  for k in starred_repos ]
	# _ = [print(f"{k.get('name')} listed: {k.get('name')  in ''.join([''.join(lists[k].get('hrefs')) for k in lists])}")  for k in starred_repos ]

if __name__ == '__main__':
	# todo add argparse
	# todo handle cache better
	asyncio.run(main())
