import requests, urllib, urllib2, time#, sys
from urlparse import urlparse
from io import BytesIO
from PIL import Image, ImageFile
from bs4 import BeautifulSoup

# hdr= {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
hdr = {"Range": "bytes=0-5119",'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}


def extract_yt_id(youtube_url, with_components=False):
	"""
	Extract the "Video ID" from a Youtube URL, useful for playing saying video in an iframe

	It does so by scanning the 'query', 'fragment' and 'path' components of a provided youtube url
	It employes different strategies for parsing 'query', 'fragment' and 'path'
	For 'query', it partitions the string along 'v=' or 'vi=', and then slices out the first 11 characters (which form the video ID)
	For 'fragment', it splits the string along '/', and retrieves the first 11 characters from the string in the last index of the resulting list
	For 'path', it splits the string along '/', and retreives the last index of the resulting list (which forms the video ID)
	"""
	vid_id = None
	raw_components = urlparse(youtube_url)
	url_query = raw_components.query
	url_path = raw_components.path
	url_fragment = raw_components.fragment
	############# handling vid_ids contained in 'query' part of urls #############
	if 'v=' in url_query:
		vid_url_components = url_query.partition("v=")
		if vid_url_components:
			vid_string = vid_url_components[2]
			if vid_string:
				# slice the first 11 characters
				vid_id = vid_string[0:11]

	elif 'vi=' in url_query:
		vid_url_components = url_query.partition("vi=")
		if vid_url_components:
			vid_string = vid_url_components[2]
			if vid_string:
				# slice the first 11 characters
				vid_id = vid_string[0:11]
	########### handling vid_ids contained in 'fragment' part of urls ###########
	elif 'p/' in url_fragment:
		frag_list = url_fragment.split("/")
		if len(frag_list) >= 4:
			# high chance this frag_list contains the video ID at the very last index
			probable_video_id = frag_list[-1]
			if len(probable_video_id) == 11:
				# handling cases where we're dealing with something lie '6dwqZw0j_jY'
				vid_id = probable_video_id
			elif len(probable_video_id) > 11:
				# handling cases where we're dealing with something like '1p3vcRhsYGo?rel=0'
				vid_id = probable_video_id[0:11]
	elif 'v=' in url_fragment:
		frag_list = url_fragment.partition("v=")
		probable_video_id = frag_list[-1]
		if len(probable_video_id) == 11:
			vid_id = probable_video_id

	############# handling vid_ids contained in 'path' part of urls #############
	else:
		path_list = url_path.split("/")
		if len(path_list) >= 2:
			# high chance this path_list contains the video ID at the very last index
			if len(path_list[-1]) == 11:
				vid_id = path_list[-1]
	
	if with_components:
		return vid_id, raw_components
	else:
		return vid_id


def get_degree_of_completeness(img_meta):
	"""
	Assigns a unique 'level' based on how complete the retrieved metadata is

	Degree of completeness (of retrieved metadata):

	'0': no metadata retrieved
	'1': just image retrieved
	'2': just title retrieved
	'3': just desc retrieved
	'4': just img and img_dim retrieved
	'5': just desc and img retrieved
	'6': just title and img retrieved
	'7': just desc and title retrieved
	'8': just title, img and img_dim retrieved
	'9': just desc, img and img_dim retrieved
	'10': just desc, title and img retrieved
	'11': desc, title, img and img_dim retrieved
	"""
	if img_meta:
		desc_exists,title_exists,img_exists,img_dim_exists = 'url_desc' in img_meta,'url_title' in img_meta,'url_img' in img_meta,'url_hw_ratio' in img_meta
		if desc_exists and title_exists and img_exists and img_dim_exists:
			return '11'
		elif desc_exists and title_exists and img_exists:
			return '10'
		elif desc_exists and img_exists and img_dim_exists:
			return '9'
		elif title_exists and img_exists and img_dim_exists:
			return '8'
		elif desc_exists and title_exists:
			return '7'
		elif title_exists and img_exists:
			return '6'
		elif img_exists and img_dim_exists:
			return '4'
		elif desc_exists and img_exists:
			return '5'
		elif desc_exists:
			return '3'
		elif title_exists:
			return '2'
		elif img_exists:
			return '1'
		else:
			return '0'#no meaningful metadata was retrieved

	else:
		return '0'#no metadata was retrieved


def get_web_img_dimensions(url):
	"""
	Returns image dimensions
	"""
	try:
		req = requests.get(url, headers=hdr,timeout=1.7)#timeout is amount of time this waits between receving bytes. It's not the total time
	except (requests.exceptions.ReadTimeout,requests.exceptions.ConnectionError,requests.exceptions.InvalidURL,requests.exceptions.MissingSchema):
		return None
	try:
		im = Image.open(BytesIO(req.content))
	except IOError:
		return None
	return im.size

	
def get_meta_data(url):
	"""
	Returns meta data of provided url
	"""
	start_time = time.time()
	try:
		response = requests.get(url,headers=hdr,timeout=1.7) # will be caught in except if timeout is reached
	except requests.exceptions.ConnectionError:
		return {'doc':'0'}, time.time() - start_time
	except (requests.exceptions.ReadTimeout,requests.exceptions.InvalidURL):
		return {}, time.time() - start_time
	except requests.exceptions.MissingSchema:
		try:
			response = requests.get('http://'+url,headers=hdr,timeout=1.7)
		except requests.exceptions.ConnectionError:
			return {'doc':'0'}, time.time() - start_time
		except (requests.exceptions.ReadTimeout,requests.exceptions.InvalidURL):
			return {},time.time() - start_time
	soup = BeautifulSoup(response.text,"lxml")
	metas = soup.find_all('meta')#list of all meta tags in the web page
	# print metas
	metadata = {}
	if metas and len(metas) > 0:
		# print "Meta tags for %s" % url
		for meta in metas:
			# print meta
			if 'name' in meta.attrs:
				if meta.attrs['name'] == 'image' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_img'] = meta.attrs['content']
				elif meta.attrs['name'] == 'title' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_title'] = meta.attrs['content']
				elif meta.attrs['name'] == 'description' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_desc'] = meta.attrs['content']
				elif meta.attrs['name'] == 'twitter:image' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_img'] = meta.attrs['content']
				elif meta.attrs['name'] == 'twitter:title' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_title'] = meta.attrs['content']
				elif meta.attrs['name'] == 'twitter:description' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_desc'] = meta.attrs['content']
				else:
					pass
			if 'property' in meta.attrs:
				if meta.attrs['property'] == 'og:image' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_img'] = meta.attrs['content']
				elif meta.attrs['property'] == 'og:title' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_title'] = meta.attrs['content']
				elif meta.attrs['property'] == 'og:description' and 'content' in meta.attrs and meta.attrs['content']:
					metadata['url_desc'] = meta.attrs['content']
				else:
					pass
			# shortcircuiting
			if 'url_img' in metadata and 'url_title' in metadata and 'url_desc' in metadata:
				break
		if 'url_title' not in metadata:
			# falling back to title tag
			titles = soup.find_all('title')
			if titles and len(titles) > 0:
				title_soup = BeautifulSoup(str(titles[0]),"lxml")
				metadata['url_title'] = title_soup.get_text()
		if 'url_desc' in metadata:
			metadata['url_desc'] = metadata['url_desc'].encode('utf-8')
		if 'url_title' in metadata:
			metadata['url_title'] = metadata['url_title'].encode('utf-8')
		if 'url_img' in metadata:
			if metadata['url_img'][0] == '/':
				# incomplete url, delete the key
				del metadata['url_img']
			else:
				image_dim = get_web_img_dimensions(metadata['url_img'])
				if image_dim:
					try:
						metadata['url_iw'], metadata['url_ih'] = image_dim[0], image_dim[1]
						metadata['url_hw_ratio'] = image_dim[1]/(image_dim[0]*1.0)
					except (IndexError,TypeError,KeyError):
						pass
	metadata['doc'] = get_degree_of_completeness(metadata)#'doc' is degree_of_completeness of metacontent, e.g. how many fields were successfuly retrieved. Useful later.
	# print metadata
	return metadata, time.time() - start_time


# if __name__=="__main__":
# 	get_meta_data()