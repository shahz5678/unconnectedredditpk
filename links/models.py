from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from math import log
from django.core.validators import MaxLengthValidator
import os
import uuid
from django.conf import settings
from django.core.files.storage import Storage
from azure.storage.blob import BlobService
accountName = 'damadam'
accountKey = 'xgYsEzkHXoRN+IsruzVOt7KJwK4iEeueomVDItV0DFSaruXlKFCvvq/kKzZevat74zbg/Hs6v+wQYicWDZF8Og=='

class OverwriteStorage(Storage):
    container = 'pictures'#settings.AZURE_STORAGE.get('CONTAINER')
    account_name = accountName
    account_key = accountKey
    #cdn_host = settings.AZURE_STORAGE.get('CDN_HOST')
    #use_ssl = settings.AZURE_STORAGE.get('USE_SSL')
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
            x_ms_blob_content_type=content_type
        )
        #print "content saved"
        content.close()
        #print "content closed"
        #url = self.url(name)
        #print "URL is: %s" % url
        #print "exiting _save"
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
        #url = '%s/%s' % (self._get_container_url(), name)
        url = '%s/%s/%s' % ('http://damadam.blob.core.windows.net','pictures', name)
        #print "name is %s" % name
        #print "url is %s" % url
        #print "exiting url"
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

def upload_avatar_to_location(instance, filename):
	try:
		blocks = filename.split('.') 
		ext = blocks[-1]
		filename = "%s.%s" % (uuid.uuid4(), ext)
		instance.title = blocks[0]
		return os.path.join('avatars/', filename)
	except Exception as e:
		print '%s (%s)' % (e.message, type(e))
		return 0

TYPE = (
('1','Tamashaee'),
('2','Gupshup'),
('3','Sports'),
('4','News'),
('5','Poetry'),
('6','Romance'),
('7','Songs'),
('8','Rishtay'),
('9', 'Lain Dain')
	)

CATEGS = (
('1','Gupshup'),
('2','Songs'),
('3','Funny'),
('4','Videos'),
('5','Cricket'),
('6','Photos'),
('7','Ajeeb'),
('8','Dosti'),
('9', 'Khareedna Baichna')
	)

STATUS = (
('1','Strangers'),
('2','Friends'),
('3','Blocked')
	)

REPLIES = (
('0','Normal'),
('1','Invite'),
('2','Kick'),
('3','Report'),
('4','Topic_Change'),
('5','Rules_Change'),
	)

'''
class Privatemsg(models.Model):
	to_user = models.ForeignKey(User)
	link = models.ForeignKey(Link)
	seen = models.BooleanField(default=False)

class Relationship(models.Model):
	status = models.CharField("Status", choices=STATUS, default=1, max_length=25)
	userone = models.ForeignKey(User, related_name='relationship_userone')
	usertwo = models.ForeignKey(User, related_name='relationship_usertwo')
	initiator = models.ForeignKey(User) #in case follow relationship has to be built
'''

class LinkVoteCountManager(models.Manager): #this class is derived from model manager
	pass
	#def get_query_set(self): #all we're doing here is over-riding get_query_set. 
		#return super(LinkVoteCountManager, self).get_query_set().annotate(votes=Sum('vote__value'))#.order_by('-rank_score', '-votes')'''
			 #using a parent-class function here, over-riding query_set to include count field
# annotate allows annotating the results of any query_set with some aggregate function like sum, count, average
class Link(models.Model):
	description = models.TextField("Kuch likho:", validators=[MaxLengthValidator(500)])
	submitter = models.ForeignKey(User) # link.submitter is a user!
	submitted_on = models.DateTimeField(auto_now_add=True)
	rank_score = models.FloatField(default=0.0)
	url = models.URLField("website (agr hai):", max_length=250, blank=True)
	cagtegory = models.CharField("Category", choices=CATEGS, default=1, max_length=25)
	image_file = models.ImageField("Tasveer dalo:",upload_to=upload_to_location, storage=OverwriteStorage(), null=True, blank=True )
	
	with_votes = LinkVoteCountManager() #change this to set_rank()
	objects = models.Manager() #default, in-built manager
	
	def __unicode__(self): # built-in function
		return self.description
		#return self.upvote+self.downvote

	def get_absolute_url(self): #this function tells your browser where to redirect to once a link has been created.
		return reverse("link_detail", kwargs={"pk": str(self.id)})

	def set_rank(self): # it seems this is run ONLY when validating models is called (pressing ctrl S after changin code)
		# Based on reddit ranking algo at http://amix.dk/blog/post/19588
		pass
		'''epoch = datetime(1970, 1, 1).replace(tzinfo=None)
		netvotes = self.votes # 'NONE' votes are messing up netvotes amount.
		if netvotes == None:
			netvotes = 0
		order = log(max(abs(netvotes), 1), 10) #0.041392685 for zero votes, log 1 = 0
		sign = 1 if netvotes > 0 else -1 if netvotes < 0 else 0
		unaware_submission = self.submitted_on.replace(tzinfo=None)
		td = unaware_submission - epoch 
		epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
		secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
		self.rank_score = round(sign * order + secs / 45000, 8)
		self.save() # this persists the rank_score in the database'''
		# the score doesn't decay as time goes by, but newer stories get a higher score over time. 

class Group(models.Model):
	topic = models.TextField("Topic dalo:", validators=[MaxLengthValidator(200)], default='Damadam ki aik karari si mehfil...', null=True)
	rules = models.TextField("Yahan ka Qanoon:", validators=[MaxLengthValidator(500)], default='Ladies ki izzat karo aur galiyan nahi do...', null=True)
	owner = models.ForeignKey(User)
	private = models.CharField("Privacy:", max_length=5, default=0)
	category = models.CharField("Category:", choices=TYPE, default=1, max_length=25)
	unique = models.CharField(max_length=36, unique=True)#for storing UUIDs
	created_at = models.DateTimeField(auto_now_add=True)
	pics_ki_ijazat = models.CharField(max_length=5, default=1)
	
	def __unicode__(self): #built-in function
		return u"%s created %s, where private is %s" % (self.owner, self.topic, self.private)

class GroupCaptain(models.Model):
	which_user = models.ForeignKey(User)
	which_group = models.ForeignKey(Group)

	def __unicode__(self):
		return u"%s was made a captain in %s" % (self.which_user, self.which_group.topic)

class GroupBanList(models.Model):
	which_user = models.ForeignKey(User)
	which_group = models.ForeignKey(Group)

	def __unicode__(self): #built-in function
		return u"%s was banned from %s" % (self.which_user, self.which_group.topic)

class HellBanList(models.Model):
	condemned = models.ForeignKey(User)
	when = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.condemned.username

class GroupTraffic(models.Model):
	visitor = models.ForeignKey(User)
	which_group = models.ForeignKey(Group)
	time = models.DateTimeField(db_index=True, auto_now_add=True)

	def __unicode__(self):
		return u"%s visited %s" % (self.visitor, self.which_group.topic)

class GroupInvite(models.Model):
	invitee = models.ForeignKey(User, related_name='invitee')
	inviter = models.ForeignKey(User, related_name ='inviter')
	sent_at = models.DateTimeField(db_index=True, auto_now_add=True)
	which_group = models.ForeignKey(Group)

	def __unicode__(self):
		return u"%s was invited to %s by %s" % (self.invitee, self.which_group.topic, self.inviter)

class Reply(models.Model):
	text = models.TextField("Likho:", validators=[MaxLengthValidator(500)])
	which_group = models.ForeignKey(Group)
	writer = models.ForeignKey(User) # reply.writer is a user!
	submitted_on = models.DateTimeField(db_index=True, auto_now_add=True)
	image = models.ImageField("Tasveer:", upload_to=upload_pic_to_location, storage=OverwriteStorage(), null=True, blank=True )
	category = models.CharField(choices=REPLIES, default='0', max_length=15)

	def __unicode__(self):
		return u"%s replied %s in group %s" % (self.writer, self.text, self.which_group.topic)

class GroupSeen(models.Model):
	seen_user = models.ForeignKey(User)
	seen_at = models.DateTimeField(auto_now_add=True)
	which_reply = models.ForeignKey(Reply)

	def __unicode__(self):
		return u"%s saw %s" % (self.seen_user, self.which_reply)

class Vote(models.Model):
	voter = models.ForeignKey(User) #what user.id voted
	link = models.ForeignKey(Link) #which link did the user vote on
	value = models.IntegerField(null=True, blank=True, default=0)

	def __unicode__(self):
		return u"%s gave %s to %s" % (self.voter.username, self.value, self.link.description)

# class SuperDownvote(models.Model):
# 	caster = models.ForeignKey(User)
# 	time = models.DateTimeField(auto_now_add=True)
# 	available = models.PositiveIntegerField(default=0)

# class SuperUpvote(models.Model):
# 	caster = models.ForeignKey(User)
# 	time = models.DateTimeField(auto_now_add=True)
# 	available = models.PositiveIntegerField(default=3)

class UserProfile(models.Model):
	user = models.OneToOneField(User, unique=True)
	bio = models.TextField("Apney baarey mein koi khaas baat batao", default='Ao gupshup lagain...', null=True)
	gender = models.CharField("Aurat ho ya mard?", max_length=10, default=1)
	age = models.PositiveIntegerField("Kitni umr hai?", null=True)
	shadi_shuda = models.CharField("Shaadi kar li hai?", max_length=10, default=0)
	previous_retort = models.CharField(blank=True, max_length=500)
	attractiveness = models.CharField("Shakal soorat", max_length=50, default=1)
	mobilenumber = models.CharField("Mobile Number ", blank=True, max_length=50) #added mobile number to model, form and __init__
	score = models.IntegerField("Score", default=0)
	avatar = models.ImageField(upload_to=upload_avatar_to_location, storage=OverwriteStorage(), null=True, blank=True )

	def __unicode__(self):
		return u"%s's profile" % self.user

class Publicreply(models.Model):
	submitted_by = models.ForeignKey(User)
	answer_to = models.ForeignKey(Link)
	submitted_on = models.DateTimeField(auto_now_add=True)
	description = models.TextField("Jawab:", validators=[MaxLengthValidator(250)])
	category = models.CharField("Category", choices=CATEGS, default=1, max_length=20)
	seen = models.BooleanField(default=False)
	abuse = models.BooleanField(default=False)

	def __unicode__(self):
		return u"%s replied %s to %s" % (self.submitted_by, self.description, self.answer_to)

def create_profile(sender, instance, created, **kwargs):
	if created:
		profile, created = UserProfile.objects.get_or_create(user=instance)

class Seen(models.Model):
	seen_status = models.BooleanField(default=False)
	seen_user = models.ForeignKey(User)
	seen_at = models.DateTimeField(auto_now_add=True)
	which_reply = models.ForeignKey(Publicreply, null=True, blank=True, related_name="publicreply_seen_related")

	def __unicode__(self):
		return u"new replies to %s were seen by %s on %s" % (self.which_reply, self.seen_user, self.seen_at)

class Unseennotification(models.Model):
	recipient = models.OneToOneField(User)
	timestamp = models.DateTimeField()

	def __unicode__(self):
		return u"%s recieved a replynotification" % self.recipient

class UserSettings(models.Model):
	user = models.OneToOneField(User, unique=True)
	score_setting = models.CharField("Sab ka score dikhao", max_length=20, default=0)
	setting2 = models.CharField("Setting2", max_length=20, default=0)
	setting3 = models.CharField("Setting3", max_length=20, default=0)
	setting4 = models.CharField("Setting4", max_length=20, default=0)
	setting5 = models.CharField("Setting5", max_length=20, default=0)

	def __unicode__(self):
		return u"%s's settings" % self.user

# Signal, while saving user
from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)

