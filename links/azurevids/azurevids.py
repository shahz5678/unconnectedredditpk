import subprocess
def uploadvid(video):
	#print video
	proc = subprocess.Popen("/usr/bin/php vodworkflow_drm_playready_widevine.php videos " \
		+str(video), shell=True, stdout=subprocess.PIPE, cwd='/home/mhb11/unconnectedredditpk/links/azurevids/')
	base_uri = ''
	acc_comp = ''
	streaming_url = ''
	list = ['b_64_000001.jpg',
	'b_180_000001.jpg',
	'b_720_000001.jpg' ]
	while True:
	  line = proc.stdout.readline()
	  if line != '':
	    #the real code does filtering here
	    if line.startswith('BASE URI:'):
	    	base_uri = line[10:].rstrip()
	    if line.startswith('ACC COMP:'):
	    	acc_comp = line[10:].rstrip()
	    if line.startswith('Streaming URL:'):
	    	streaming_url = line[15:].rstrip()
	    # print line.rstrip()
	  else:
	    break
	a = [base_uri +'/'+s+acc_comp  for s in list]
	a.insert(3,streaming_url)
	return a