from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django_extensions.db.fields import RandomCharField
from datetime import datetime
from math import log
from django.core.validators import MaxLengthValidator, MaxValueValidator, URLValidator
from django.conf import settings
from imagestorage import OverwriteStorage, upload_to_location, upload_pic_to_location, upload_chatpic_to_location, upload_avatar_to_location, \
upload_photo_to_location, upload_photocomment_to_location
from videostorage import OverwriteVideoStorage, upload_video_to_location

PHOTOS = (
('1','Islam'),
('2','Funny'),
('3','Shairi'),
('4','Sports'),
('5','Masala'),
('6','Style'),
('7','Selfies'),
('8','Nail Color'),
('9', 'Halat-e-hazra'),
	)

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
('1','Chat'),
('2','Mehfil'),
('3','Kings'),
('4','Zalmi'),
('5','Qalandars'),
('6','Photos'),
('7','Gladiators'),
('8','United')
	)

ORIGINS = (
('1','Chupair'),
('2','Publicreply'),
('3','Nickname'),
('4','Profile'),
('5','Mehfilkick'),
('6','Mehfilreport'),
('7','Photocomment'),
('8','Photovote')
	)

VIDEOS = (
('1','Funny'),
('2','Celebs'),
('3','Ads'),
('4','Personal'),
('5','Religious'),
('6','Song'),
('7','Animals'),
('8','Babies')
	)

DEVICE = (
('1','Feature'),
('2','Smartphone'),
('3','Laptop'),
('4','Tablet'),
('5','Other')
	)

STATUS = (
('1','Strangers'),
('2','Friends'),
('3','Blocked')
	)

OBJECTS = (
('0','Comments'),
('1','Fans'),
('2','Links'),
('3','Groups'),
('4','Salat')
	)

LIFETIME = (
('1','Finite'),
('2','Infinite'),	
('3','User Decided')
	)

SALAT = (
('1','Fajr'),
('2','Zuhr'),
('3','Asr'),
('4','Maghrib'),
('5','Isha'),
	)

REPLIES = (
('0','Normal'),
('1','Invite'),
('2','Kick'),
('3','Report'),
('4','Topic_Change'),
('5','Rules_Change'),
('6','Left'),
('7','Unaccepted Invite'),
	)

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
	is_visible = models.BooleanField(default=True)
	device = models.CharField(choices=DEVICE, default='1', max_length=10)
	which_photostream = models.ForeignKey('links.PhotoStream', null=True, blank=True)
	reply_count = models.IntegerField(default=0)
	net_votes = models.IntegerField(default=0) #only counts votes, for censorship purposes
	url = models.URLField("website (agr hai):", max_length=250, blank=True)
	cagtegory = models.CharField("Category", choices=CATEGS, default=1, max_length=25)
	image_file = models.ImageField("Photo charhao:",upload_to=upload_to_location, storage=OverwriteStorage(), null=True, blank=True )
	latest_reply = models.ForeignKey('links.Publicreply', blank=True, null=True, on_delete=models.CASCADE)#models.SET_NULL)
	
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

class PhotoCooldown(models.Model):
	which_user = models.ForeignKey(User)
	time_of_uploading = models.DateTimeField(db_index=True) #regenerate a trial after 1 min.

class PhotoStream(models.Model):
	cover = models.ForeignKey('links.Photo')
	creation_time = models.DateTimeField(auto_now_add=True)
	show_time =  models.DateTimeField(db_index=True)
	photo_count = models.IntegerField(default=1)

	def __unicode__(self):
		return u"A photostream was created at %s" % self.creation_time

class Photo(models.Model):
	owner = models.ForeignKey(User)
	which_stream = models.ManyToManyField(PhotoStream)
	image_file = models.ImageField(upload_to=upload_photo_to_location, storage=OverwriteStorage())
	upload_time = models.DateTimeField(auto_now_add=True, db_index=True)
	comment_count = models.IntegerField()
	is_public = models.BooleanField(default=True) #in case user wants to upload private photos too
	vote_score = models.IntegerField(default=0) #only counts vote score, for censorship purposes
	visible_score = models.IntegerField(default=0)
	invisible_score = models.FloatField(default=0.0) #for use when time-decay is factored in
	caption = models.CharField("Privacy:", max_length=100, null=True, default=None)
	avg_hash = models.CharField(max_length=16, default=None)
	latest_comment = models.ForeignKey('links.PhotoComment', blank=True, null=True, on_delete=models.CASCADE, related_name="latest")
	second_latest_comment = models.ForeignKey('links.PhotoComment', blank=True, null=True, on_delete=models.CASCADE, related_name="second_latest")
	category = models.CharField(choices=PHOTOS, default='1', max_length=11)
	device = models.CharField(choices=DEVICE, default='1', max_length=10)

	def __unicode__(self):
		return u"%s uploaded a photo" % self.owner

	class Meta:
		ordering = ['-id', '-upload_time', '-comment_count']

	def set_rank(self): # it seems this is run ONLY when validating models is called (pressing ctrl S after changin code)
		# Based on reddit ranking algo at http://amix.dk/blog/post/19588
		epoch = datetime(1970, 1, 1).replace(tzinfo=None)
		netvotes = self.visible_score # 'NONE' votes are messing up netvotes amount.
		if netvotes == None:
			netvotes = 0
		order = log(max(abs(netvotes), 1), 10) #0.041392685 for zero votes, log 1 = 0
		sign = 1 if netvotes > 0 else -1 if netvotes < 0 else 0
		unaware_submission = self.upload_time.replace(tzinfo=None)
		td = unaware_submission - epoch 
		epoch_submission = td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000) #number of seconds from epoch till date of submission
		secs = epoch_submission - 1432201843 #a recent date, coverted to epoch time
		self.invisible_score = round(sign * order + secs / 45000, 8)
		score = self.invisible_score
		#self.save() # this persists the invisible_score in the database
		return score
		# the score doesn't decay as time goes by, but newer stories get a higher score over time. 

class PhotoVote(models.Model):
	voter = models.ForeignKey(User, related_name='voter') #what user.id voted
	photo = models.ForeignKey(Photo) #which photo did the user vote on
	photo_owner = models.ForeignKey(User, related_name='photo_owner')
	value = models.IntegerField(null=True, blank=True, default=0)

	def __unicode__(self):
		return u"%s gave %s to %s" % (self.voter.username, self.value, self.photo.caption)

class HotUser(models.Model):
	which_user = models.OneToOneField(User, unique=True)
	hot_score = models.IntegerField(default=0, db_index=True)
	allowed = models.BooleanField(default=False)
	updated_at = models.DateTimeField()

class PhotoComment(models.Model):
	which_photo = models.ForeignKey(Photo)
	text = models.TextField("Jawab:", validators=[MaxLengthValidator(250)])
	device = models.CharField(choices=DEVICE, default='1', max_length=10)
	submitted_by = models.ForeignKey(User)
	submitted_on = models.DateTimeField(auto_now_add=True)
	image_comment = models.ImageField(upload_to=upload_photocomment_to_location, storage=OverwriteStorage())
	has_image = models.BooleanField(default=False)
	abuse = models.BooleanField(default=False)

	def __unicode__(self):
		return u"%s commented on a photo, saying: %s" % (self.submitted_by, self.text)

class Video(models.Model):
	owner = models.ForeignKey(User)
	small_thumb = models.TextField(validators=[URLValidator()], null=True, default=None)
	low_res_thumb = models.TextField(validators=[URLValidator()], null=True, default=None)
	#high_res_thumb = models.TextField(validators=[URLValidator()], null=True, default=None)
	low_res_video = models.TextField(validators=[URLValidator()], null=True, default=None)
	high_res_video = models.TextField(validators=[URLValidator()], null=True, default=None)
	video_file = models.FileField(upload_to=upload_video_to_location, storage=OverwriteVideoStorage())
	category = models.CharField(choices=VIDEOS, default='1', max_length=11)
	device = models.CharField(choices=DEVICE, default='1', max_length=10)
	is_public = models.BooleanField(default=True) #in case user wants to upload private videos too
	processed = models.BooleanField(default=False) #waiting for video to finish processing
	caption = models.CharField("Privacy:", max_length=100, null=True, default=None)
	vote_score = models.IntegerField(default=0) #only counts vote score, for censorship purposes
	visible_score = models.IntegerField(default=0)
	invisible_score = models.FloatField(default=0.0) #for use when time-decay is factored in
	comment_count = models.IntegerField()
	upload_time = models.DateTimeField(auto_now_add=True, db_index=True)
	latest_comment = models.ForeignKey('links.VideoComment', blank=True, null=True, on_delete=models.CASCADE, related_name="latest")
	second_latest_comment = models.ForeignKey('links.VideoComment', blank=True, null=True, on_delete=models.CASCADE, related_name="second_latest")
	
	def __unicode__(self):
		return u"%s uploaded a video" % self.owner

class VideoComment(models.Model):
	which_video = models.ForeignKey(Video)
	text = models.TextField(validators=[MaxLengthValidator(250)])
	device = models.CharField(choices=DEVICE, default='1', max_length=10)
	submitted_by = models.ForeignKey(User)
	submitted_on = models.DateTimeField(auto_now_add=True)
	abuse = models.BooleanField(default=False)

	def __unicode__(self):
		return u"%s commented on a video, saying: %s" % (self.submitted_by, self.text)

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

class TotalFanAndPhotos(models.Model):
	owner = models.OneToOneField(User, unique=True)
	total_photos = models.IntegerField(default=0)
	total_fans = models.IntegerField(default=0)
	last_updated = models.DateTimeField(db_index=True)

class UserFan (models.Model):
	star = models.ForeignKey(User, related_name='star')
	fan = models.ForeignKey(User, related_name='fan')
	fanning_time = models.DateTimeField(db_index=True)

	def __unicode__(self):
		return u"%s became a fan of %s" % (self.fan, self.star)

class SalatInvite(models.Model):
	invitee = models.ForeignKey(User, related_name='salat_invitee')
	inviter = models.ForeignKey(User, related_name ='salat_inviter')
	sent_at = models.DateTimeField(db_index=True)
	which_salat = models.CharField(db_index=True, choices=SALAT, max_length = 8)

	def __unicode__(self):
		return u"%s invited %s for prayer %s" % (self.inviter, self.invitee, self.which_salat)

class GroupInvite(models.Model):
	invitee = models.ForeignKey(User, related_name='invitee')
	inviter = models.ForeignKey(User, related_name ='inviter')
	sent_at = models.DateTimeField(db_index=True, auto_now_add=True)
	which_group = models.ForeignKey(Group)

	def __unicode__(self):
		return u"%s was invited to %s by %s" % (self.invitee, self.which_group.topic, self.inviter)

class Logout(models.Model):
	logout_user = models.ForeignKey(User)
	logout_time = models.DateTimeField(auto_now_add=True)
	pre_logout_score = models.IntegerField(null=True, blank=True, default=0)

	def __unicode__(self):
		return u"%s logged out at %s, dropping score to 10 from %s" % (self.logout_user,self.logout_time,self.pre_logout_score)

class Reply(models.Model):
	text = models.TextField("Likho:",db_index=True, validators=[MaxLengthValidator(500)])
	which_group = models.ForeignKey(Group)
	writer = models.ForeignKey(User) # reply.writer is a user!
	submitted_on = models.DateTimeField(db_index=True, auto_now_add=True)
	image = models.ImageField("Tasveer:", upload_to=upload_pic_to_location, storage=OverwriteStorage(), null=True, blank=True )
	device = models.CharField(choices=DEVICE, default='1', max_length=10)
	category = models.CharField(db_index=True,choices=REPLIES, default='0', max_length=15)

	def __unicode__(self):
		return u"%s replied %s in group %s" % (self.writer, self.text, self.which_group.topic)

class PhotoObjectSubscription(models.Model):
	viewer = models.ForeignKey(User)
	updated_at = models.DateTimeField(db_index=True)
	seen = models.BooleanField(default=True, db_index=True)
	type_of_object = models.CharField(choices=OBJECTS, default='0', max_length=15)
	which_photo = models.ForeignKey(Photo, null=True, blank=True)
	which_link = models.ForeignKey(Link, null=True, blank=True)
	which_group = models.ForeignKey(Group, null=True, blank=True)
	which_salat = models.ForeignKey(SalatInvite, null=True, blank=True)

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

class Cooldown(models.Model):
	voter = models.ForeignKey(User)
	time_of_casting = models.DateTimeField() #Max 10 votes, regenerate a vote after 30 mins.
	hot_score = models.IntegerField(default=0, validators=[MaxValueValidator(12)])

class LatestSalat(models.Model):
	salatee = models.ForeignKey(User)
	latest_salat = models.CharField(choices=SALAT, max_length = 8)
	when = models.DateTimeField()
	skipped = models.BooleanField(default=False)

class Salat(models.Model):
	prayee = models.ForeignKey(User)
	which_salat = models.CharField(choices=SALAT, max_length = 8)
	timing = models.DateTimeField()

	def __unicode__(self):
		return u"%s offered %s" % (self.prayee, self.which_salat)

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
	streak = models.IntegerField("Streak", default=0, db_index=True)
	media_score = models.IntegerField("Media Score", default=0)
	avatar = models.ImageField(upload_to=upload_avatar_to_location, storage=OverwriteStorage(), null=True, blank=True )

	def __unicode__(self):
		return u"%s's profile" % self.user

class Report(models.Model):
	reporter = models.ForeignKey(User, related_name='reporter')
	target = models.ForeignKey(User, related_name ='target')
	report_origin = models.CharField(db_index=True, choices=ORIGINS, default=1, max_length=20)
	report_reason = models.TextField(blank=True, validators=[MaxLengthValidator(500)])
	reported_at = models.DateTimeField(db_index=True, auto_now_add=True)
	which_link = models.ForeignKey(Link, null=True, blank=True)
	which_publicreply = models.ForeignKey('links.Publicreply', null=True, blank=True)
	which_photo = models.ForeignKey(Photo, null=True, blank=True)
	which_photocomment = models.ForeignKey(PhotoComment, null=True, blank=True)
	which_group = models.ForeignKey(Group, null=True, blank=True)
	which_reply = models.ForeignKey(Reply, null=True, blank=True)

class Publicreply(models.Model):
	submitted_by = models.ForeignKey(User)
	answer_to = models.ForeignKey(Link)
	submitted_on = models.DateTimeField(auto_now_add=True)
	description = models.TextField("Jawab:", validators=[MaxLengthValidator(250)])
	category = models.CharField("Category", choices=CATEGS, default=1, max_length=20)
	device = models.CharField(choices=DEVICE, default='1', max_length=10)
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

class TutorialFlag(models.Model):
	user = models.OneToOneField(User, unique=True)
	seen_chain = models.BooleanField(default=False)
	seen_photo_option = models.BooleanField(default=False)
	seen_fan_option = models.BooleanField(default=False)
	seen_salat_option = models.BooleanField(default=False)
	seen_special_photo_option = models.BooleanField(default=False)

class UserSettings(models.Model):
	user = models.OneToOneField(User, unique=True)
	score_setting = models.CharField("Sab ka score dikhao", max_length=20, default=0)
	setting2 = models.CharField("Setting2", max_length=20, default=0)
	setting3 = models.CharField("Setting3", max_length=20, default=0)
	setting4 = models.CharField("Setting4", max_length=20, default=0)
	setting5 = models.CharField("Setting5", max_length=20, default=0)

	def __unicode__(self):
		return u"%s's settings" % self.user

class ChatPic(models.Model):
	image = models.ImageField("Tasveer lagao:", upload_to=upload_chatpic_to_location, storage=OverwriteStorage())
	owner = models.ForeignKey(User)
	upload_time = models.DateTimeField(db_index=True, auto_now_add=True)
	times_sent = models.IntegerField(default=0)
	is_visible = models.BooleanField(default=True)
	unique = models.CharField(max_length=36, unique=True)

	def __unicode__(self):
		return u"new ChatPic was uploaded by %s at %s" % (self.owner, self.upload_time)

class ChatPicMessage(models.Model):
	which_pic = models.ForeignKey(ChatPic)
	sender = models.ForeignKey(User)
	viewing_time = models.DateTimeField()
	sending_time = models.DateTimeField(auto_now_add=True)
	what_number = models.CharField(max_length=50)
	expiry_interval = models.CharField(choices=LIFETIME, default='1', max_length=15)
	caption = models.CharField("Paigham:", blank=True, max_length=150)
	seen = models.BooleanField(default=False)

	def __unicode__(self):
		return u"a ChatPicMessage was formed at %s, with expiry set to %s" % (self.sending_time, self.expiry_interval)

class ChatInbox(models.Model):
	pin_code = RandomCharField(length=4, unique=True, include_alpha=False)
	owner = models.ForeignKey(User)
	creation_time = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return u"new ChatInbox was created for %s at %s with pin %s" % (self.owner, self.creation_time, self.pin_code)

# Signal, while saving user
from django.db.models.signals import post_save
post_save.connect(create_profile, sender=User)

