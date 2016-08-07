import PIL
from PIL import Image
import uuid, StringIO, string, os
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.storage import Storage
from azure.storage.blob import BlobService

accountName = 'damadam'
accountKey = 'xgYsEzkHXoRN+IsruzVOt7KJwK4iEeueomVDItV0DFSaruXlKFCvvq/kKzZevat74zbg/Hs6v+wQYicWDZF8Og=='

class OverwriteStorage(Storage):
	container = 'pictures'#settings.AZURE_STORAGE.get('CONTAINER')
	account_name = accountName
	account_key = accountKey
	#cdn_host = settings.AZURE_STORAGE.get('CDN_HOST')
	def __init__(self, account_name=None, account_key=None, container=None):

		if account_name is not None:
			self.account_name = account_name

		if account_key is not None:
			self.account_key = account_key

		if container is not None:
			self.container = container
	def __getstate__(self):
		return dict(
			account_name=self.account_name,
			account_key=self.account_key,
			container=self.container
		)
	def _save(self,name,content):
		blob_service = BlobService(account_name=accountName, account_key=accountKey)
		import mimetypes
		small_content = content
		content.open()
		content_type = None
		if hasattr(content.file, 'content_type'):
			content_type = content.file.content_type
		else:
			content_type = mimetypes.guess_type(name)[0]
		content_str = content.read()
		blob_service.put_blob(
			'pictures',
			name,
			content_str,
			x_ms_blob_type='BlockBlob',
			x_ms_blob_content_type=content_type,
			x_ms_blob_cache_control ='public, max-age=3600, s-maxage=86400' #cache in the browser for 1 hr, on the edge for 24 hrs
		)
		content.close()
		if "avatars" in name: #creating and saving thumbnail
			small_image_name = name
			small_image_name = string.replace(small_image_name, "avatars", "thumbnails")
			thumbnail = StringIO.StringIO()
			size = 22, 22
			image = small_content.file		
			image = Image.open(image)
			small_image = image.resize(size, Image.ANTIALIAS)
			small_image.save(thumbnail,'JPEG',quality=70, optimize=True)
			img = InMemoryUploadedFile(thumbnail, None, 'small.jpg', 'image/jpeg', thumbnail.len, None)
			small_content.file = img
			small_content.open()
			stream = small_content.read()
			blob_service.put_blob(
				'pictures',
				small_image_name,
				stream,
				x_ms_blob_type='BlockBlob',
				x_ms_blob_content_type=content_type,
				x_ms_blob_cache_control ='public, max-age=604800, s-maxage=604800' #cache in the browser and on the edge for 7 days
			)
			small_content.close()
		elif "photos" in name:
			small_image_name = name
			small_image_name = string.replace(small_image_name, "photos", "thumbnails")
			thumbnail = StringIO.StringIO()
			#size = 40, 40
			height = 38
			image = small_content.file		
			image = Image.open(image)
			wpercent = (height/float(image.size[1]))
			bsize = int((float(image.size[0])*float(wpercent)))
			small_image = image.resize((bsize,height), PIL.Image.ANTIALIAS)
			small_image.save(thumbnail,'JPEG',quality=70, optimize=True)
			img = InMemoryUploadedFile(thumbnail, None, 'small.jpg', 'image/jpeg', thumbnail.len, None)
			small_content.file = img
			small_content.open()
			stream = small_content.read()
			blob_service.put_blob(
				'pictures',
				small_image_name,
				stream,
				x_ms_blob_type='BlockBlob',
				x_ms_blob_content_type=content_type,
				x_ms_blob_cache_control ='public, max-age=3600, s-maxage=86400' #cache in the browser for 1 hr, on the edge for 24 hrs
			)
			small_content.close()
		else: 
			pass
		return name
	def get_available_name(self,name):
		#print "exiting get_available_name"
		return name
	def _get_service(self):
		if not hasattr(self, '_blob_service'):
			self._blob_service = BlobService(
				account_name=self.account_name,
				account_key=self.account_key,
				protocol='http'
			)
		#print "exiting _get_service"    
		return self._blob_service
	def _open(self, name, mode='rb'):
		"""
		Return the AzureStorageFile.
		"""
		from django.core.files.base import ContentFile
		contents = self._get_service().get_blob(self.container, name)
		#print "exiting _open"
		return ContentFile(contents)
	def _get_properties(self, name):
		#print "exiting _get_properties"
		return self._get_service().get_blob_properties(
			self.container,
			name
		)
	def _get_container_url(self):
		if not hasattr(self, '_container_url'):
			base_url = 'http://{host}/{container}'
			#if self.cdn_host:
			#    base_url = self.cdn_host
			self._container_url = base_url.format({
				#'protocol': 'http',
				'host': self._get_service()._get_host(),
				'container': self.container,
			})
		#print "exiting _get_container_url"
		return self._container_url
	def url(self, name):
		"""
		Returns the URL where the contents of the file referenced by name can
		be accessed.
		"""
		url = '%s/%s/%s' % ('//damadam.blob.core.windows.net','pictures', name)
		return url

def upload_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('links/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0

def upload_pic_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('mehfils/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0

def upload_chatpic_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('picschat/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0

def upload_avatar_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1] #whether jpg or png
		filename = "%s.%s" % (uuid.uuid4(), ext) #giving a uuid name to the image
		instance.title = blocks[0]
		return os.path.join('avatars/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0

def upload_photo_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1] #whether jpg or png
		filename = "%s.%s" % (uuid.uuid4(), ext) #giving a uuid name to the image
		instance.title = blocks[0]
		return os.path.join('photos/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0

def upload_photocomment_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1] #whether jpg or png
		filename = "%s.%s" % (uuid.uuid4(), ext) #giving a uuid name to the image
		instance.title = blocks[0]
		return os.path.join('photos/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0