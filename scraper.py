#inspired by and a derivate of reddit's scraper.py
from bs4 import BeautifulSoup
from django.core.validators import URLValidator
from urlparse import urlparse, urljoin
from django.core.exceptions import ValidationError
import urllib2, re, requests, sys, StringIO
from urllib2 import Request, urlopen
from PIL import Image, ImageFile
from io import BytesIO
import os, httplib2, math
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")

urlv = URLValidator()
bytes_read = 0
thumbnail_size = 70, 70
hdr= {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}

def final_url(url):
	h = httplib2.Http(".cache_httplib")
	h.follow_all_redirects = True
	resp = h.request(url, "GET")[0]
	contentLocation = resp['content-location']
	return contentLocation
'''
def unshorten_url(url):
	parse_object = urlparse(url)
	h = httplib.HTTPConnection(parse_object.netloc)
	h.request('HEAD', parse_object.path)
	response = h.getresponse()
	print response
	print url
	if response.status/100 == 3 and response.getheader('Location'):
		return unshorten_url(response.getheader('Location'))
	else:
		return url
'''
def parse_url(url):
	global bytes_read
	#r = requests.get(url)
	#bytes_read = bytes_read + sys.getsizeof(r)
	#url = r.url
	parse_object = urlparse(url)
	if not parse_object.scheme:
		url = "http://"+url
	#url = urlnorm.norm(url)
	#url = final_url(url)
	#print url
	try:
		#url = urllib2.urlopen(url).geturl()
		req = urllib2.Request(url, None, headers=hdr)
		webpage = urllib2.urlopen(req) #urllib2 is an http library
		content_type = webpage.headers.get('content-type')
		bytes_read = bytes_read + sys.getsizeof(webpage)
		if 'image' in content_type:
			return (url, 0)
		soup = BeautifulSoup(webpage, "lxml")
		return (url, soup)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return (0, 0)

def clean_url(url):
	"""url quotes unicode data out of urls"""
	s = url
	url = s.encode('utf8')
	url = ''.join([urllib.quote(c) if ord(c) >= 127 else c for c in url])
	return url

def image_sizing(string, url):
	RANGE = 5000
	src = string.get("src")
	clean_src = clean_url(src)
	global bytes_read
	try:
		urlv(clean_src)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		clean_src = urljoin(url, clean_src)
	try:
		req  = requests.get(clean_src,headers={'User-Agent':'Mozilla5.0(Google spider)','Range':'bytes=0-{}'.format(RANGE)})#requests is an HTTP library
		bytes_read = bytes_read + sys.getsizeof(req)
		dimensions = Image.open(BytesIO(req.content))#bytesIO is a simple stream of in-memory bytes, open doesn't load image
		#print dimensions.size
		return (dimensions, clean_src)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return (None, None)	

def return_largest_image(url):
	normal_url, soup = parse_url(url)
	#print normal_url
	max_area = 0
	max_dimensions = None
	max_clean_src = None
	previous_max_src = None
	if normal_url:
		if soup:
			for img in soup.findAll('img', src=True)[:40]:
				my_dimensions, my_clean_src = image_sizing(img, normal_url)
				print my_clean_src
				try:
					if my_dimensions.height/my_dimensions.width>1.5:#ignore banner like images
						continue
					if my_dimensions.width/my_dimensions.height>1.5:#ignore banner like images
						continue
					if my_dimensions.height * my_dimensions.width < 5001:#ignore small images
						continue
					area = my_dimensions.height * my_dimensions.width
					if area > max_area:
						max_area = area
						#print 'assigning previous'
						previous_max_src = max_clean_src #assigning previously biggest image to previous_max_src
						max_dimensions = my_dimensions
						max_clean_src = my_clean_src
				except Exception as e:
					print '%s (%s)' % (e.message, type(e))
					continue	
		else:
			max_clean_src = normal_url #if soup = 0, the url is an image url
	#if max_clean_src: print max_clean_src
	#if max_dimensions: print max_dimensions
	return (max_clean_src, previous_max_src)
	
def image_entropy(img):
	"""calculate the entropy of an image"""
	hist = img.histogram()
	hist_size = sum(hist)
	hist = [float(h) / hist_size for h in hist]
	return -sum([p * math.log(p, 2) for p in hist if p != 0])

def square_image(img):
	"""if the image is taller than it is wide, square it off. determine
	which pieces to cut off based on the entropy pieces."""
	x,y = img.size
	while y > x:
		#slice 10px at a time until square
		slice_height = min(y - x, 10)
		bottom = img.crop((0, y - slice_height, x, y))
		top = img.crop((0, 0, x, slice_height))
		#remove the slice with the least entropy
		if image_entropy(bottom) < image_entropy(top):
			img = img.crop((0, 0, x, y - slice_height))
		else:
			img = img.crop((0, slice_height, x, y))
		x,y = img.size
	return img

def prep_image(image):
	image = square_image(image)
	global thumbnail_size
	try:
		image.thumbnail(thumbnail_size)#, Image.ANTIALIAS)
		print 'successfully thumbnailed'
		return image
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0


def str_to_image(s):
	s = StringIO.StringIO(s)
	s.seek(0)
	image = Image.open(s)
	return image

def read_image(url):
	src, second = return_largest_image(url)
	#print src
	#print second
	global bytes_read
	if src:
		try:
			name = urlparse(src).path.split('/')[-1]
			open_req = urlopen(src)
			bytes_read = bytes_read + sys.getsizeof(open_req)
			content = open_req.read()
			bytes_read = bytes_read + sys.getsizeof(content)
			print bytes_read
			image = str_to_image(content)
			image = prep_image(image)
			return (name,image)
		except:
			try:
				name = urlparse(second).path.split('/')[-1]
				open_req = urlopen(second)#if first image return a 403 error
				bytes_read = bytes_read + sys.getsizeof(open_req)
				content = open_req.read()
				bytes_read = bytes_read + sys.getsizeof(content)
				print bytes_read
				image = str_to_image(content)
				image = prep_image(image)
				return (name,image)
			except Exception as e:
				print '%s (%s)' % (e.message, type(e))
				return (None, None)
			print '%s (%s)' % (e.message, type(e))
			return (None, None)
	else:
		#print 'No image to read'
		return (None, None)

if __name__=="__main__":
		read_image()