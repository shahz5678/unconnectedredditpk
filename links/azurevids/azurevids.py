import subprocess
def uploadvid(video):
	#print video
	proc = subprocess.Popen("/usr/bin/php vodworkflow_drm_playready_widevine.php videos " \
		+str(video), shell=True, stdout=subprocess.PIPE, cwd='/home/hassan/Desktop/unconnectedredditpk/links/azurevids/')
	base_uri = ''
	acc_comp = ''
	list = ['b_64_000001.jpg',
	'b_180_000001.jpg',
	'b_720_000001.jpg',
	'b_320x180_400.mp4',
	'b_1280x720_3400.mp4' ]
	while True:
	  line = proc.stdout.readline()
	  if line != '':
	    #the real code does filtering here
	    if line.startswith('BASE URI:'):
	    	base_uri = line[10:].rstrip()
	    if line.startswith('ACC COMP:'):
	    	acc_comp = line[10:].rstrip()
	    print line.rstrip()
	  else:
	    break
	return [base_uri +'/'+s+acc_comp for s in list]