import random, string, re
from django import forms
from django.core.exceptions import ValidationError
from models import GroupTraffic, Group, Reply
from redis4 import get_and_delete_text_input_key, is_limited, many_short_messages, log_short_message
from forms import repetition_found, human_readable_time, uniform_string
from redis6 import is_topic_change_frozen, human_readable_time, topic_change_rate_limited, log_topic_change, log_topic_changing_attempt,\
is_rules_change_frozen, rules_change_rate_limited,log_rules_changing_attempt, log_rules_change
from score import PRIVATE_GROUP_MAX_TITLE_SIZE, PRIVATE_GROUP_COST, PUBLIC_GROUP_COST, PUBLIC_GROUP_MAX_TITLE_SIZE, \
PUBLIC_GROUP_MAX_RULES_SIZE
from abuse import BANNED_MEHFIL_TOPIC_WORDS, BANNED_MEHFIL_RULES_WORDS


##################### Utility Functions ########################################
def number_new_lines(text):
	"""
	Adds 'numbering' to text (beginning of each new line)

	Useful when presenting 'rules' of a mehfil to users
	"""
	# lines, counter = text.splitlines(), 1
	# if len(lines) > 1:
	#   formatted_text = ''
	#   for line in lines:
	#       if line:
	#           line = str(counter)+". "+line.strip()+"\n"
	#           formatted_text += line
	#           counter += 1
	#   return formatted_text
	# else:
	#   # do not add 'numbering' if only 1 line exists
	return text

def spot_gibberish_or_repeating_text_in_rules(text,length_of_text, user_id=None):
	if length_of_text > 15 and ' ' not in text:
		log_rules_changing_attempt(user_id)
		raise ValidationError('Rules mein khali space dalein')
	else:
		tokens = text[:12].split()
		if len(tokens) > 1:
			first_word = tokens[0]
			len_first_word = len(first_word)
			offset = text[len_first_word:].find(first_word)
			if offset > -1:
				first_start = len_first_word+offset
				first_end = first_start+len_first_word
				first_repetition = text[first_start:first_end]
				if first_word == first_repetition:
					second_start = first_end + offset
					second_end = second_start+len_first_word
					second_repetition = text[second_start:second_end]
					if first_repetition == second_repetition:
						third_start = second_end + offset
						third_end = third_start + len_first_word
						third_repetition = text[third_start:third_end]
						if third_repetition == second_repetition:
							log_rules_changing_attempt(user_id)
							raise ValidationError('Rules mein cheezain repeat nahi karein')

def validate_rules_chars(rules, user_id=None):
	"""
	Performs validation checks on mehfil rules
	"""
	reg = re.compile('^[\w\s.?\-%()\$,;:!\'"]+$')
	if not reg.match(rules):
		raise ValidationError('Rules mein sirf english words, numbers ya ! ? % $ _ . , ; : ( ) - " \' characters likhein')
	for word in BANNED_MEHFIL_RULES_WORDS:
		if word in rules.lower():
			log_rules_changing_attempt(user_id)# rate limit the user if too many of these words are attempted
			raise ValidationError('Rules mein "%s" nahi likhein' % word.capitalize())

def process_group_rules(rules, rules_len_threshold, user_id=None, unique=None, group_id=None):
	"""
	Processes rules setting for OpenGroupCreateForm() and ChangeGroupRulesForm() (e.g.validation etc.)

	unique is 'None' if the public mehfil is yet to be created
	"""
	rules_change_frozen = is_rules_change_frozen(group_id) if group_id else False
	if rules_change_frozen:
		raise forms.ValidationError('Sorry! Ye mehfil report ho chuki hai aur investigation puri honay tak rules change nahi kiye ja saktey')
	else:
		ttl = rules_change_rate_limited(user_id,unique)
		if ttl:
			raise forms.ValidationError('Ap rules {} baad change kar sakein ge'.format(human_readable_time(ttl)))
		else:
			len_rules = len(rules)
			if not rules:
				raise forms.ValidationError('Rules likhna zaruri hain')
			elif len_rules < 4:
				raise forms.ValidationError('Rules itnay chotay nahi ho saktay')
			elif len_rules > rules_len_threshold:
				raise forms.ValidationError('Rules {0} chars se lambay nahi hota. Ap ne {1} chars likhey'.format(rules_len_threshold,len_rules))
			elif rules.isdigit():
				raise forms.ValidationError('Rules mein sirf numbers nahi ho saktey')
			validate_rules_chars(rules, user_id)
			spot_gibberish_or_repeating_text_in_rules(rules,len_rules, user_id)
			uni_str = uniform_string(rules)
			if uni_str:
				if uni_str.isspace():
					log_rules_changing_attempt(user_id)
					raise forms.ValidationError('Ziyada khali spaces daal di hain')
				else:
					log_rules_changing_attempt(user_id)
					raise forms.ValidationError('"%s" - is terhan bar bar letters repeat nahi karein' % uni_str)
			log_rules_change(user_id,unique)

def validate_topic_chars(topic, user_id=None):
	"""
	Performs validation checks on mehfil topic
	"""
	reg = re.compile('^[\w\s.?\-%()\$,;:!\'"]+$')
	if not reg.match(topic):
		raise ValidationError('Topic mein sirf english words, numbers ya ! ? % $ _ . , ; : ( ) - " \' characters likhein')
	for word in BANNED_MEHFIL_TOPIC_WORDS:
		if word in topic.lower():
			log_topic_changing_attempt(user_id)# rate limit the user if too many of these words are attempted
			raise ValidationError('Topic mein "%s" nahi likhein' % word.capitalize())

def spot_gibberish_or_repeating_text_in_topic(text,length_of_text, user_id=None):
	if length_of_text > 15 and ' ' not in text:
		log_topic_changing_attempt(user_id)
		raise ValidationError('Topic mein khali space dalein')
	else:
		tokens = text[:12].split()
		if len(tokens) > 1:
			first_word = tokens[0]
			len_first_word = len(first_word)
			offset = text[len_first_word:].find(first_word)
			if offset > -1:
				first_start = len_first_word+offset
				first_end = first_start+len_first_word
				first_repetition = text[first_start:first_end]
				if first_word == first_repetition:
					second_start = first_end + offset
					second_end = second_start+len_first_word
					second_repetition = text[second_start:second_end]
					if first_repetition == second_repetition:
						third_start = second_end + offset
						third_end = third_start + len_first_word
						third_repetition = text[third_start:third_end]
						if third_repetition == second_repetition:
							log_topic_changing_attempt(user_id)
							raise ValidationError('Topic mein cheezain repeat nahi karein')

def process_group_topic(topic, topic_len_threshold, user_id=None, unique=None, how_long='short', group_id=None):
	"""
	Processes topic setting for OpenGroupCreateForm(), ChangePrivateGroupTopicForm() and ChangeGroupTopicForm() (e.g.validation etc.)

	unique is 'None' if the public mehfil is yet to be created
	"""
	topic_change_frozen = is_topic_change_frozen(group_id) if group_id else False
	if topic_change_frozen:
		raise forms.ValidationError('Sorry! Ye mehfil report ho chuki hai aur investigation puri honay tak topic change nahi kiya ja sakta')
	else:
		ttl = topic_change_rate_limited(user_id,unique)
		if ttl:
			raise forms.ValidationError('Ap topic {} baad change kar sakein ge'.format(human_readable_time(ttl)))
		else:
			len_topic = len(topic)
			if not topic:
				raise forms.ValidationError('Topic rakhna zaruri hai')
			elif len_topic < 4:
				raise forms.ValidationError('Topic itna chota nahi ho sakta')
			elif len_topic > topic_len_threshold:
				raise forms.ValidationError('Topic {0} chars se lamba nahi hota. Ap ne {1} chars likhey'.format(topic_len_threshold,len_topic))
			elif topic.isdigit():
				raise forms.ValidationError('Topic mein sirf numbers nahi ho saktey')
			validate_topic_chars(topic, user_id)
			spot_gibberish_or_repeating_text_in_topic(topic,len_topic, user_id)
			uni_str = uniform_string(topic)
			if uni_str:
				if uni_str.isspace():
					log_topic_changing_attempt(user_id)
					raise forms.ValidationError('Ziyada khali spaces daal di hain')
				else:
					log_topic_changing_attempt(user_id)
					raise forms.ValidationError('"%s" - is terhan bar bar letters repeat nahi karein' % uni_str)
			log_topic_change(user_id,unique,how_long=how_long)


class GroupHelpForm(forms.Form):
	class Meta:
		pass

class ReinviteForm(forms.Form):
	class Meta:
		pass

class OpenGroupHelpForm(forms.Form):
	class Meta:
		pass

class ClosedGroupHelpForm(forms.Form):
	class Meta:
		pass

class MehfilForm(forms.Form):
	class Meta:
		pass

class AppointCaptainForm(forms.Form): #doesn't work as forms.ModelForm
	class Meta:
		pass

class OwnerGroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class GroupOnlineKonForm(forms.ModelForm):
	class Meta:
		model = GroupTraffic

class DirectMessageCreateForm(forms.Form):
	class Meta:
		model = Group

class ClosedGroupCreateForm(forms.ModelForm):
	"""
	Validates topic in private mehfils (at the point of their creation)
	"""
	topic = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PRIVATE_GROUP_MAX_TITLE_SIZE}),\
	error_messages={'required': 'Topic likhna zaruri hai'})
	class Meta:
		model = Group
		exclude = ("owner","created_at", "members", "cagtegory","private", "rules", "pics_ki_ijazat")
		fields = ("topic",)

	def __init__(self, *args, **kwargs):
		self.score = kwargs.pop('score',None)
		super(ClosedGroupCreateForm, self).__init__(*args, **kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:98%;height:100px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_topic(self):
		user_score = self.score
		if user_score >= PRIVATE_GROUP_COST:
			topic = self.cleaned_data.get("topic")
			topic = topic.strip()
			process_group_topic(topic, topic_len_threshold=PRIVATE_GROUP_MAX_TITLE_SIZE)# no need to send over user_id or unique_id (the latter doesn't even exist)
			return string.capwords(topic)
		else:
			raise forms.ValidationError('Ye mehfil {0} points se banti hai, apka score {1} hai'.format(PRIVATE_GROUP_COST,user_score))


class OpenGroupCreateForm(forms.ModelForm):
	"""
	Validates all required fields of public mehfils at the point of their creation
	"""
	CATEGS = (
		('2','Haan'),#open to pink stars only
		('1','Nahi'),#open to everyone
		)
	
	topic = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PUBLIC_GROUP_MAX_TITLE_SIZE}),\
	error_messages={'required': 'Topic likhna zaruri hai'})
	rules = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off','autocorrect':'off',\
		'autocapitalize':'off','spellcheck':'false','maxlength':PUBLIC_GROUP_MAX_RULES_SIZE}),error_messages={'required': 'Rules likhna zaruri hain'})
	category = forms.TypedChoiceField(required=False, choices=CATEGS, initial='1', widget=forms.RadioSelect, coerce=int,\
		error_messages={'required': '"Haan" ya "Nahi" ka intekhab karein'})

	class Meta:
		model = Group
		exclude = ("owner","private","created_at","pics_ki_ijazat")
		fields = ("topic","rules","category")

	def __init__(self, *args, **kwargs):
		self.is_mob_verified = kwargs.pop('verified',None)
		self.score = kwargs.pop('score',None)
		self.rejoin = kwargs.pop('rejoin',None)
		super(OpenGroupCreateForm, self).__init__(*args, **kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:98%;height:100px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'
		self.fields['rules'].widget.attrs['style'] = 'width:98%;height:250px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_topic(self):
		is_mob_verified, user_score, is_rejoining = self.is_mob_verified, self.score, self.rejoin
		if (is_mob_verified and user_score >= PUBLIC_GROUP_COST) or (is_mob_verified and is_rejoining):
			topic = self.cleaned_data.get("topic")
			topic = topic.strip()
			process_group_topic(topic, topic_len_threshold=PUBLIC_GROUP_MAX_TITLE_SIZE)# no need to send over user_id or unique_id (the latter doesn't even exist)
			return string.capwords(topic)
		elif user_score < PUBLIC_GROUP_COST:
			raise forms.ValidationError('Ye mehfil {0} points se banti hai, apka score {1} hai'.format(PUBLIC_GROUP_COST,user_score))
		else:
			raise forms.ValidationError('Mobile number verify kiye beghair public mehfil nahi banti')

	def clean_rules(self):
		is_mob_verified, user_score, is_rejoining = self.is_mob_verified, self.score, self.rejoin
		if (is_mob_verified and user_score >= PUBLIC_GROUP_COST) or (is_mob_verified and is_rejoining):
			rules = self.cleaned_data.get("rules")
			rules = rules.strip()
			process_group_rules(rules, rules_len_threshold=PUBLIC_GROUP_MAX_RULES_SIZE)
			return number_new_lines(rules), rules
		elif user_score < PUBLIC_GROUP_COST:
			raise forms.ValidationError('Ye mehfil {0} points se banti hai, apka score {1} hai'.format(PUBLIC_GROUP_COST,user_score))
		else:
			raise forms.ValidationError('Mobile number verify kiye beghair public mehfil nahi banti')


class DirectMessageForm(forms.Form):
	class Meta:
		pass        

class ReinvitePrivateForm(forms.Form):
	class Meta:
		pass

class GroupListForm(forms.Form):
	class Meta:
		pass

class GroupTypeForm(forms.Form):
	class Meta:
		pass

class ChangeGroupRulesForm(forms.ModelForm):
	rules = forms.CharField(label='Neya Qanoon:', widget=forms.Textarea(attrs={'cols':40,'rows':3,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("rules",)

class ChangePrivateGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='New Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

	def clean_topic(self):
		topic = self.cleaned_data.get("topic")
		topic = topic.strip()
		# topic = clear_zalgo_text(topic)
		if not topic:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		elif topic < 1:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		return topic


class ChangeGroupTopicForm(forms.ModelForm):
	topic = forms.CharField(label='Neya Topic:', widget=forms.Textarea(attrs={'cols':30,'rows':2,'style':'width:98%;'}))
	class Meta:
		model = Group
		fields = ("topic",)

	def clean_topic(self):
		topic = self.cleaned_data.get("topic")
		topic = topic.strip()
		# topic = clear_zalgo_text(topic)
		if not topic:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		elif topic < 1:
			raise forms.ValidationError('Topic rakhna zaruri hai')
		return topic

class PublicGroupReplyForm(forms.ModelForm):
	text = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':40,'rows':3,'autofocus': 'autofocus',\
		'class': 'cxl','autocomplete': 'off','autocapitalize':'off','spellcheck':'false'}),error_messages={'required': 'tip: likhna zaruri hai'})
	image = forms.ImageField(required=False,error_messages={'invalid_image': 'tip: photo sahi nahi hai'})
	sk = forms.CharField(required=False)
	gp = forms.IntegerField()

	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.is_mob_verified = kwargs.pop('is_mob_verified',None)
		super(PublicGroupReplyForm, self).__init__(*args,**kwargs)
		# self.fields['image'].widget.attrs['accept'] = 'image/*'
		self.fields['image'].widget.attrs['id'] = 'pub_grp_browse_image_btn'
		self.fields['text'].widget.attrs['id'] = 'pub_grp_text_field'
		self.fields['text'].widget.attrs['style'] = 'width:99%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		text, user_id, section_id, section, image, secret_key_from_form = data.get("text"), self.user_id, data.get("gp"), 'pub_grp', \
		data.get('image'), data.get('sk')
		secret_key_from_session = get_and_delete_text_input_key(self.user_id,section_id,'pub_grp')
		text = text.strip() if text else text # make function sophisticated https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('tip: sirf aik dafa button dabain')
	
		elif not text:
			if image:
				rate_limited, reason = is_limited(user_id,section='pub_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap open mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				elif not self.is_mob_verified:
					raise forms.ValidationError('tip: yahan foto laganey ke liye apna mobile number verify karwain')
				else:
					data["text"] = random.choice(["... ... ...",".. .. ..","... .. ...",".. ... ..","... ... ..",".. ... ...",". ... .",\
						". . . . .",".. .. .. ..",".... . ....","... .... ..."]) # for aesthetic reasons
					return data
			else:
				raise forms.ValidationError('tip: likhna zaruri hai')
		else:
			if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
			else:
				rate_limited, reason = is_limited(user_id,section='pub_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap open mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					text_len = len(text)
					# if text_len < 1:
					#   raise forms.ValidationError('tip: likhna zaruri hai')
					# elif text_len < 2:
					#   raise forms.ValidationError('tip: itni choti baat nahi likh sakte')
					if text_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('tip: har thori deir baad yahan choti baat nah likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif text_len > 500:
						raise forms.ValidationError('tip: itni barri baat nahi likh sakte')
					if not self.is_mob_verified:
						raise forms.ValidationError('tip: yahan likhne ke liye apna mobile number verify karwain')
					# text = clear_zalgo_text(text)
					# uni_str = uniform_string(text)
					# if uni_str:
					#   if uni_str.isspace():
					#       raise forms.ValidationError('tip: ziyada spaces daal di hain')
					#   else:
					#       raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likhein' % uni_str)
					data["text"] = text
					return data

class PrivateGroupReplyForm(forms.ModelForm):
	text = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':40,'rows':3,'autofocus': 'autofocus','class': 'cxl',\
		'autocomplete': 'off','autocapitalize':'off','spellcheck':'false'}),error_messages={'required': 'tip: likhna zaruri hai'})
	image = forms.ImageField(required=False,error_messages={'invalid_image': 'tip: photo sahi nahi hai'})
	sk = forms.CharField(required=False)
	gp = forms.IntegerField()
	
	class Meta:
		model = Reply
		exclude = ("submitted_on","which_group","writer","abuse")
		fields = ("image", "text")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		super(PrivateGroupReplyForm, self).__init__(*args,**kwargs)
		self.fields['text'].widget.attrs['style'] = 'width:99%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		text, user_id, section_id, section, image, secret_key_from_form = data.get("text"), self.user_id, data.get("gp"), 'prv_grp', \
		data.get("image"), data.get("sk")
		secret_key_from_session = get_and_delete_text_input_key(self.user_id,section_id,'prv_grp')
		text = text.strip() if text else text
		if not text:
			if image:
				rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					data["text"] = random.choice(["... ... ...",".. .. ..","... .. ...",".. ... ..","... ... ..",".. ... ...",". ... .",\
						". . . . .",".. .. .. ..",".... . ....","... .... ..."]) # for aesthetic reasons
					return data
			else:
				raise forms.ValidationError('tip: likhna zaruri hai')
		elif secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('tip: sirf aik dafa button dabain')
		else:
			if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('tip: milti julti baatien nah likho, kuch new likho')
			else:
				rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				else:
					text_len = len(text)
					if text_len < 1:
						raise forms.ValidationError('tip: likhna zaruri hai')
					# elif text_len < 2:
					#   raise forms.ValidationError('tip: itni choti baat nahi likh sakte')
					if text_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('tip: har thori deir baad yahan choti baat nah likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif text_len > 500:
						raise forms.ValidationError('tip: itni barri baat nahi likh sakte')
					# text = clear_zalgo_text(text)
					# uni_str = uniform_string(text)
					# if uni_str:
					#   if uni_str.isspace():
					#       raise forms.ValidationError('tip: ziyada spaces daal di hain')
					#   else:
					#       raise forms.ValidationError('tip: "%s" ki terhan bar bar ek hi harf nah likho' % uni_str)
					data["text"] = text
					return data

