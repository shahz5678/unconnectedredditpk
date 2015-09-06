from bs4 import BeautifulSoup
from django.core.validators import URLValidator
from urlparse import urlparse, urljoin
from django.core.exceptions import ValidationError
import urllib2, re, requests, sys, urlnorm, StringIO
from urllib2 import Request, urlopen
from PIL import Image, ImageFile
from io import BytesIO

#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unconnectedreddit.settings")

urlv = URLValidator()
bytes_read = 0
thumbnail_size = 70, 70

def parse_url(url):
	global bytes_read
	parse_object = urlparse(url)
	if not parse_object.scheme:
		url = "http://"+url
	url = urlnorm.norm(url)
	print url
	try:
		webpage = urllib2.urlopen(url) #urllib2 is an http library
		soup = BeautifulSoup(webpage, "lxml")
		bytes_read = bytes_read + sys.getsizeof(webpage)
		return (url, soup)
	except:
		print "Can't open URL for BeautifulSoup"
		return 0

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
	except:
		print 'URL not valid'
		clean_src = urljoin(url, clean_src)
	try:
		req  = requests.get(clean_src,headers={'Range':'bytes=0-{}'.format(RANGE)})#requests is an HTTP library
		bytes_read = bytes_read + sys.getsizeof(req)
		dimensions = Image.open(BytesIO(req.content))#bytesIO is a simple stream of in-memory bytes, open doesn't load image
		print dimensions.size
		return (dimensions, clean_src)
	except:
		return (None, None)	

def return_largest_image(url):
	normal_url, soup = parse_url(url)
	max_area = 0
	max_dimensions = None
	max_clean_src = None
	if soup:
		for img in soup.findAll('img', src=True):
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
					max_dimensions = my_dimensions
					max_clean_src = my_clean_src
			except:
				continue
	if max_clean_src: print max_clean_src
	if max_dimensions: print max_area
	return max_clean_src
	
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
		print 'success'
	except:
		print "Can't convert to thumbnail"
		return 0
	return image

def str_to_image(s):
	s = StringIO.StringIO(s)
	s.seek(0)
	image = Image.open(s)
	return image

def read_image():
	src = return_largest_image('wwe.com')
	global bytes_read
	if src:
		try:
			open_req = urlopen(src)
			bytes_read = bytes_read + sys.getsizeof(open_req)
			content = open_req.read()
			bytes_read = bytes_read + sys.getsizeof(content)
			print bytes_read
			image = str_to_image(content)
			image = prep_image(image)
			

		except:
			print 'Something went wrong'
	else:
		print 'No image to read'

if __name__=="__main__":
        read_image()