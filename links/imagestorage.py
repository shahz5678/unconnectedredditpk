import PIL
from PIL import Image
# from boto.s3.connection import S3Connection
# from boto.s3.key import Key
import uuid, StringIO, string, os, mimetypes
from storages.backends.s3boto import S3BotoStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from unconnectedreddit.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_LOCATION#, AWS_STORAGE_BUCKET
from score import THUMB_HEIGHT


os.environ['S3_USE_SIGV4'] = 'True'



def upload_image_to_s3(image, prefix='1on1/'):
	"""
	Used by views for 1on1 and mehfil photos
	"""
	image_name_with_path = os.path.join(prefix, "%s.jpg" % uuid.uuid4())
	s3_object = S3Storage()
	return s3_object._save(name=image_name_with_path, content=image)


##########################################################
##########################################################


def upload_to_picschat(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('picschat/', filename)
	except Exception as e:
		# print '%s (%s)' % (e.message, type(e))
		return 0


def upload_to_mehfils(instance, filename):
	pass
	# try:
	# 	blocks = filename.split('.') 
	# 	ext = blocks[-1] #whether jpg or png
	# 	filename = "%s.%s" % (uuid.uuid4(), ext) #giving a uuid name to the image
	# 	instance.title = blocks[0]
	# 	return os.path.join('mehfils/', filename)
	# except Exception as e:
	# 	# print '%s (%s)' % (e.message, type(e))
	# 	return 0


def upload_to_avatars(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1] #whether jpg or png
		filename = "%s.%s" % (uuid.uuid4(), ext) #giving a uuid name to the image
		instance.title = blocks[0]
		return os.path.join('avatar/', filename)
	except Exception as e:
		# print '%s (%s)' % (e.message, type(e))
		return 0

def upload_to_photos(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('public/', filename)
	except Exception as e:
		# print '%s (%s)' % (e.message, type(e))
		return 0


def upload_to_links(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('links/', filename)
	except Exception as e:
		# print '%s (%s)' % (e.message, type(e))
		return 0


def upload_to_photocomments(instance, filename):
	pass
	# try:
	# 	blocks = filename.split('.') 
	# 	ext = blocks[-1] #whether jpg or png
	# 	filename = "%s.%s" % (uuid.uuid4(), ext) #giving a uuid name to the image
	# 	instance.title = blocks[0]
	# 	return os.path.join('photos/', filename)
	# except Exception as e:
	# 	# print '%s (%s)' % (e.message, type(e))
	# 	return 0


def get_thumb(filename, content, folder_name):
	"""
	Creates thumbs out of images passed into it
	"""
	thumb_name = string.replace(filename, folder_name, "thumb/"+folder_name)
	image = content.file		
	image = Image.open(image)
	if folder_name == 'avatar':
		size = 22, 22
	elif folder_name == 'public' or folder_name == '1on1':
		height = THUMB_HEIGHT
		image = content.file		
		image = Image.open(image)
		wpercent = (height/float(image.size[1]))
		bsize = int((float(image.size[0])*float(wpercent)))
		size = (bsize,height)
	small_image = image.resize(size, Image.ANTIALIAS)
	thumbnail = StringIO.StringIO()
	small_image.save(thumbnail,'JPEG',quality=70, optimize=True)
	img = InMemoryUploadedFile(thumbnail, None, 'small.jpg', 'image/jpeg', thumbnail.len, None)
	content.file = img
	return thumb_name, content


class S3Storage(S3BotoStorage):	

	acc_key = AWS_ACCESS_KEY_ID
	sec_key = AWS_SECRET_ACCESS_KEY
	calling_format = 'boto.s3.connection.OrdinaryCallingFormat'

	@property
	def connection(self):
		if self._connection is None:
			self._connection = self.connection_class(
				self.acc_key, self.sec_key,
				calling_format=self.calling_format, host=AWS_S3_LOCATION)
		return self._connection


	def _save(self, name, content):
		cleaned_name = self._clean_name(name)
		name = self._normalize_name(cleaned_name)
		headers = self.headers.copy()
		content_type = getattr(content, 'content_type',
			mimetypes.guess_type(name)[0] or self.key_class.DefaultContentType)
		# setting the content_type in the key object is not enough.
		headers.update({'Content-Type': content_type})

		if self.gzip and content_type in self.gzip_content_types:
			content = self._compress_content(content)
			headers.update({'Content-Encoding': 'gzip'})

		content.name = cleaned_name
		encoded_name = self._encode_name(name)
		key = self.bucket.get_key(encoded_name)
		if not key:
			key = self.bucket.new_key(encoded_name)
		if self.preload_metadata:
			self._entries[encoded_name] = key
		key.set_metadata('Content-Type', content_type)
		self._save_content(key, content, headers=headers)
		if 'public' in encoded_name:
			thumb_name, thumb_content = get_thumb(encoded_name, content, 'public')
			thumb_key = self.bucket.get_key(thumb_name)
			if not thumb_key:
				thumb_key = self.bucket.new_key(thumb_name)
		elif 'avatar' in encoded_name:
			thumb_name, thumb_content = get_thumb(encoded_name, content, 'avatar')
			thumb_key = self.bucket.get_key(thumb_name)
			if not thumb_key:
				thumb_key = self.bucket.new_key(thumb_name)
		elif '1on1' in encoded_name:
			thumb_name, thumb_content = get_thumb(encoded_name, content, '1on1')
			thumb_key = self.bucket.get_key(thumb_name)
			if not thumb_key:
				thumb_key = self.bucket.new_key(thumb_name)
		else:
			thumb_key = None
		if thumb_key:
			if self.preload_metadata:
				self._entries[encoded_name] = key
			key.set_metadata('Content-Type', content_type)
			self._save_content(thumb_key, thumb_content, headers=headers)
		return cleaned_name


	def _save_content(self, key, content, headers):
		kwargs = {}
		if self.encryption:
			kwargs['encrypt_key'] = self.encryption
		key.set_contents_from_file(content, headers=headers,
								   policy=self.default_acl,
								   reduced_redundancy=self.reduced_redundancy,
								   rewind=True, **kwargs)


