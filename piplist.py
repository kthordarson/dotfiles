import pkg_resources
from subprocess import call

localpacks = [k for k in pkg_resources.working_set if 'kth' in k.location]
# packages = [dist.project_name for dist in pkg_resources.working_set]
# call("pip3 -vvv install --upgrade " + ' '.join(packages), shell=True)
# call("pip install -v --upgrade --user" + ' '.join(packages), shell=True)
localcount = len(localpacks)
idx = 0
for project in localpacks:
	pack = project.project_name
	print(f'[local] {idx}/{localcount} p:{pack}')
	# call(f'pip install -v --upgrade --user {pack} ', shell=True)
	idx += 1

