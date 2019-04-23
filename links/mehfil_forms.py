import random, re, string
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from verified import FEMALES
from views import convert_to_epoch
from redis3 import invalid_topic_logger, invalid_rules_logger
from forms import repetition_found, uniform_string, clear_zalgo_text
from abuse import BANNED_MEHFIL_TOPIC_WORDS, BANNED_MEHFIL_RULES_WORDS
from redis4 import many_short_messages, get_and_delete_text_input_key, is_limited, log_short_message
from redis6 import human_readable_time, retrieve_group_creation_time, retrieve_group_privacy, retrieve_group_category, is_group_member_and_rules_signatory,\
group_ownership_transfer_blocked_by_rate_limit, ownership_request_rate_limit, is_topic_change_frozen, is_rules_change_frozen, log_topic_change,\
log_topic_changing_attempt, topic_change_rate_limited, log_rules_change, log_rules_changing_attempt, rules_change_rate_limited, group_member_exists
from score import PRIVATE_GROUP_MAX_TITLE_SIZE, PUBLIC_GROUP_MAX_TITLE_SIZE, PUBLIC_GROUP_MAX_RULES_SIZE, \
GROUP_FEEDBACK_SIZE, PUBLIC_GROUP_REPLY_LENGTH, PRIVATE_GROUP_REPLY_LENGTH, PUBLIC_GROUP_MAX_SELLING_PRICE, PUBLIC_GROUP_MIN_SELLING_PRICE, \
USER_AGE_AFTER_WHICH_PUBLIC_MEHFIL_CAN_BE_CREATED, GROUP_AGE_AFTER_WHICH_IT_CAN_BE_TRANSFERRED, PUBLIC_GROUP_OFFICER_APPLICATION_ANSWER_LEN, \
MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC

def number_new_lines(text):
	"""
	Adds 'numbering' to text (beginning of each new line)

	Useful when presenting 'rules' of a mehfil to users
	"""
	lines, counter = text.splitlines(), 1
	if len(lines) > 1:
		formatted_text = ''
		for line in lines:
			if line:
				line = str(counter)+". "+line.strip()+"\n"
				formatted_text += line
				counter += 1
		return formatted_text
	else:
		# do not add 'numbering' if only 1 line exists
		return text


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
			invalid_rules_logger(word,rules)
			raise ValidationError('Rules mein "%s" nahi likhein' % word.capitalize())


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


def disallow_multiple_occurences(text):
	"""
	Limits puntuation usage in mehfil topics (for readability)
	"""
	if text.count('.') > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '.'
	elif text.count('-') > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '-'
	elif text.count('_') > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '_'
	elif text.count("$") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '$'
	elif text.count(":") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return ':'
	elif text.count(",") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return ','
	elif text.count("(") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '('
	elif text.count(")") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return ')'
	elif text.count("?") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '?'
	elif text.count("%") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '%'
	elif text.count(";") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return ';'
	elif text.count("!") > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '!'
	elif text.count('"') > MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC:
		return '"'



def disallow_sequential_occurences(text):
	"""
	Limits sequential occurences in mehfil topics (for readability)
	"""
	if '..' in text:
		return '..'
	elif ',,' in text:
		return ',,'
	elif "$$" in text:
		return '$$'
	elif '--' in text:
		return '--'
	elif '__' in text:
		return '__'
	elif '::' in text:
		return '::'
	elif ';;' in text:
		return ';;'
	elif '._' in text:
		return '._'
	elif '_.' in text:
		return '_.'
	elif '-_' in text:
		return '-_'
	elif '_-' in text:
		return '_-'
	elif '.-' in text:
		return '.-'
	elif '-.' in text:
		return '-.'
	elif ':;' in text:
		return ':;'
	elif ';:' in text:
		return ';:'
	elif ',.' in text:
		return ',.'
	elif '.,' in text:
		return '.,'
	elif ':.' in text:
		return ':.'
	elif '.:' in text:
		return '.:'
	elif ':,' in text:
		return ':,'
	elif ',:' in text:
		return ',:'


def validate_topic_chars(topic, user_id=None):
	"""
	Performs validation checks on mehfil topic
	"""
	reg = re.compile('^[\w\s.?\-%()\$,;:!\'"]+$')
	if not reg.match(topic):
		raise ValidationError('Topic mein sirf english words, numbers ya ! ? % $ _ . , ; : ( ) - " \' characters likhein')
	else:
		disallowed_char = disallow_multiple_occurences(topic)
		if disallowed_char:
			raise ValidationError("Topic mein '{0}' {1} se ziyada dafa nahi likhein".format(disallowed_char, \
				MAX_PUNCTUATION_REPETITIONS_IN_MEHFIL_TOPIC))
		else:
			disallowed_sequence = disallow_sequential_occurences(topic)
			if disallowed_sequence:
				raise ValidationError("Topic mein '{0}' nahi likhein".format(disallowed_sequence))
			else: 
				for word in BANNED_MEHFIL_TOPIC_WORDS:
					if word in topic.lower():
						log_topic_changing_attempt(user_id)# rate limit the user if too many of these words are attempted
						invalid_topic_logger(word,topic)
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


####################################################################################################################
####################################################################################################################

class PrivateGroupReplyForm(forms.Form):
	"""
	Handles form entry and validation in private mehfils

	Turn to regular form if getting rid of Reply model
	"""
	text = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':40,'rows':3,'autofocus': 'autofocus','class': 'cxl',\
		'autocomplete': 'off','autocapitalize':'off','spellcheck':'false','maxlength':PRIVATE_GROUP_REPLY_LENGTH}),\
	error_messages={'required': 'tip: likhna zaruri hai'})
	image = forms.ImageField(required=False,error_messages={'invalid_image': 'tip: photo sahi nahi hai'})
	sk = forms.CharField(required=False)
	wid = forms.IntegerField(required=False)
	gp = forms.IntegerField()
	
	# class Meta:
	#     model = Reply
	#     exclude = ("submitted_on","which_group","writer","abuse")
	#     fields = ("image", "text")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.is_mob_verified = kwargs.pop('is_mob_verified',None)
		super(PrivateGroupReplyForm, self).__init__(*args,**kwargs)
		self.fields['image'].widget.attrs['id'] = 'grp_browse_image_btn'
		self.fields['text'].widget.attrs['id'] = 'grp_text_field'
		self.fields['text'].widget.attrs['style'] = 'width:98%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		text, user_id, section_id, section, image, secret_key_from_form, writer_id = data.get("text"), self.user_id, data.get("gp"), 'prv_grp', \
		data.get("image"), data.get("sk"), data.get('wid')
		secret_key_from_session = get_and_delete_text_input_key(self.user_id,section_id,'prv_grp')
		text = text.strip() if text else text # make function sophisticated https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('Page expire ho gaya hai, dubara post karein')
		elif text:
			if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('Milti julti baatien nahi post karein')
			else:
				rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				elif not self.is_mob_verified:
					raise forms.ValidationError('Yahan post karney ke liye apna mobile number verify karwain')
				else:
					text_len = len(text)
					if text_len < 1:
						raise forms.ValidationError('tip: likhna zaruri hai')
					if text_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('Har thori deir baad yahan choti baat nahi likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif text_len > PRIVATE_GROUP_REPLY_LENGTH:
						raise forms.ValidationError('tip: itni barri baat nahi likh sakte')
					data["text"] = text
					return data
		else:
			if image:
				rate_limited, reason = is_limited(user_id,section='prv_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap private mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				elif not self.is_mob_verified:
					raise forms.ValidationError('Yahan post karney ke liye apna mobile number verify karwain')
				else:
					data["text"] = random.choice(["... ... ...",".. .. ..","... .. ...",".. ... ..","... ... ..",".. ... ...",". ... .",\
						". . . . .",".. .. .. ..",".... . ....","... .... ..."]) # for aesthetic reasons
					return data
			else:
				if writer_id and writer_id != -1:
					raise forms.ValidationError('Pehlay yahan message likhein, phir us nickname ke agey "@" ka nishan dabain jisko yeh message bhejna hai')
				else:
					raise forms.ValidationError('tip: likhna zaruri hai')


class PublicGroupReplyForm(forms.Form):
	"""
	Handles form entry and validation in public mehfils

	Turn to regular form if getting rid of Reply model
	"""
	text = forms.CharField(required=False,widget=forms.Textarea(attrs={'cols':40,'rows':3,'autofocus': 'autofocus',\
		'class': 'cxl','autocomplete': 'off','autocapitalize':'off','spellcheck':'false','maxlength':PUBLIC_GROUP_REPLY_LENGTH}),\
	error_messages={'required': 'tip: likhna zaruri hai'})
	image = forms.ImageField(required=False,error_messages={'invalid_image': 'tip: photo sahi nahi hai'})
	sk = forms.CharField(required=False)
	wid = forms.IntegerField(required=False)
	gp = forms.IntegerField()

	# class Meta:
	#     model = Reply
	#     exclude = ("submitted_on","which_group","writer","abuse")
	#     fields = ("image", "text")

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.is_mob_verified = kwargs.pop('is_mob_verified',None)
		super(PublicGroupReplyForm, self).__init__(*args,**kwargs)
		self.fields['image'].widget.attrs['id'] = 'grp_browse_image_btn'
		self.fields['text'].widget.attrs['id'] = 'grp_text_field'
		self.fields['text'].widget.attrs['style'] = 'width:98%;height:50px;border-radius:10px;border: 1px #E0E0E0 solid; background-color:#FAFAFA;padding:5px;'

	def clean(self):
		data = self.cleaned_data
		text, user_id, section_id, section, image, secret_key_from_form, writer_id = data.get("text"), self.user_id, data.get("gp"), 'pub_grp', \
		data.get('image'), data.get('sk'), data.get('wid')
		secret_key_from_session = get_and_delete_text_input_key(self.user_id,section_id,'pub_grp')
		text = text.strip() if text else text # make function sophisticated https://stackoverflow.com/questions/1546226/simple-way-to-remove-multiple-spaces-in-a-string
		if secret_key_from_form != secret_key_from_session:
			raise forms.ValidationError('Page expire ho gaya hai, dubara post karein')
		elif text:
			if repetition_found(section=section,section_id=section_id,user_id=user_id, target_text=text):
				raise forms.ValidationError('Milti julti baatien nahi post karein')
			else:
				rate_limited, reason = is_limited(user_id,section='pub_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap public mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				elif not self.is_mob_verified:
					raise forms.ValidationError('Yahan post karney ke liye apna mobile number verify karwain')
				else:
					text_len = len(text)
					if text_len < 6:
						if many_short_messages(user_id,section,section_id):
							raise forms.ValidationError('Har thori deir baad yahan choti baat nahi likhein')
						else:
							log_short_message(user_id,section,section_id)
					elif text_len > PUBLIC_GROUP_REPLY_LENGTH:
						raise forms.ValidationError('tip: itni barri baat nahi likh sakte')
					data["text"] = text
					return data
		else:
			if image:
				rate_limited, reason = is_limited(user_id,section='pub_grp',with_reason=True)
				if rate_limited > 0:
					raise forms.ValidationError('Ap public mehfils mein likhne se {0} tak banned ho. Reason: {1}'.format(human_readable_time(rate_limited),reason))
				elif not self.is_mob_verified:
					raise forms.ValidationError('Yahan post karney ke liye apna mobile number verify karwain')
				else:
					data["text"] = random.choice(["... ... ...",".. .. ..","... .. ...",".. ... ..","... ... ..",".. ... ...",". ... .",\
						". . . . .",".. .. .. ..",".... . ....","... .... ..."]) # for aesthetic reasons
					return data
			else:
				if writer_id and writer_id != -1:
					raise forms.ValidationError('Pehlay yahan message likhein, phir us nickname ke agey "@" ka nishan dabain jisko yeh message bhejna hai')
				else:
					raise forms.ValidationError('tip: likhna zaruri hai')


class ChangePrivateGroupTopicForm(forms.Form):
	"""
	Validates new topic entered in private mehfil
	"""
	topic = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off',\
		'autofocus': 'autofocus','autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PRIVATE_GROUP_MAX_TITLE_SIZE}),\
	error_messages={'required': 'Topic likhna zaruri hain'})
	# class Meta:
	#     model = Group
	#     fields = ("topic",)

	def __init__(self,*args,**kwargs):
		self.unique = kwargs.pop('unique',None)
		self.user_id = kwargs.pop('user_id',None)
		self.group_id = kwargs.pop('group_id',None)
		super(ChangePrivateGroupTopicForm, self).__init__(*args,**kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:98%;height:70px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_topic(self):
		group_id, user_id = self.group_id, self.user_id
		if group_member_exists(group_id, user_id):
			topic = self.cleaned_data.get("topic")
			topic, unique = topic.strip(), self.unique
			process_group_topic(topic, topic_len_threshold=PRIVATE_GROUP_MAX_TITLE_SIZE, user_id=user_id, unique=unique, how_long='short', group_id=group_id)
			return string.capwords(topic)
		else:
			raise forms.ValidationError('Topic change karney ke liye ye mehfil join karein')


class ChangeGroupTopicForm(forms.Form):
	"""
	Validates new topic entered in public mehfil
	"""
	topic = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off',\
		'autofocus': 'autofocus','autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PUBLIC_GROUP_MAX_TITLE_SIZE}),\
	error_messages={'required': 'Topic likhna zaruri hain'})
	# class Meta:
	#     model = Group
	#     fields = ("topic",)

	def __init__(self,*args,**kwargs):
		self.unique = kwargs.pop('unique',None)
		self.user_id = kwargs.pop('user_id',None)
		self.group_id = kwargs.pop('group_id',None)
		super(ChangeGroupTopicForm, self).__init__(*args,**kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:98%;height:70px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_topic(self):
		group_id, topic = self.group_id, self.cleaned_data.get("topic")
		topic = topic.strip()
		user_id, unique = self.user_id, self.unique
		process_group_topic(topic, topic_len_threshold=PUBLIC_GROUP_MAX_TITLE_SIZE, user_id=user_id, unique=unique, how_long='long', group_id=group_id)
		return string.capwords(topic)


class ChangeGroupRulesForm(forms.Form):
	"""
	Validates new rules entered in public mehfil
	"""
	rules = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PUBLIC_GROUP_MAX_RULES_SIZE}),\
	error_messages={'required': 'Rules likhna zaruri hain'})
	# class Meta:
	#     model = Group
	#     fields = ("rules",)

	def __init__(self, *args, **kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.unique_id = kwargs.pop('unique_id',None)
		self.group_id = kwargs.pop('group_id',None)
		super(ChangeGroupRulesForm, self).__init__(*args, **kwargs)
		self.fields['rules'].widget.attrs['style'] = 'width:98%;height:170px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_rules(self):
		group_id, user_id, unique_id = self.group_id, self.user_id, self.unique_id
		rules = self.cleaned_data.get("rules")
		rules = rules.strip()
		process_group_rules(rules, rules_len_threshold=PUBLIC_GROUP_MAX_RULES_SIZE, user_id=user_id, unique=unique_id, group_id=group_id)
		return number_new_lines(rules), rules
	

class ClosedGroupCreateForm(forms.Form):
	"""
	Validates topic in private mehfils (at the point of their creation)
	"""
	topic = forms.CharField(widget=forms.Textarea(attrs={'cols':30,'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':PRIVATE_GROUP_MAX_TITLE_SIZE}),\
	error_messages={'required': 'Topic likhna zaruri hai'})

	def __init__(self, *args, **kwargs):
		self.is_verified = kwargs.pop('is_verified',None)
		super(ClosedGroupCreateForm, self).__init__(*args, **kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:98%;height:100px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_topic(self):
		if self.is_verified:
			topic = self.cleaned_data.get("topic")
			topic = topic.strip()
			process_group_topic(topic, topic_len_threshold=PRIVATE_GROUP_MAX_TITLE_SIZE)# no need to send over user_id or unique_id (the latter doesn't even exist)
			return string.capwords(topic)
		else:
			raise forms.ValidationError('Ye mehfil create karney ke liye apna account verify karwain')


class OpenGroupCreateForm(forms.Form):
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

	def __init__(self, *args, **kwargs):
		self.is_mob_verified = kwargs.pop('verified',None)
		# self.score = kwargs.pop('score',None)
		self.rejoin = kwargs.pop('rejoin',None)
		super(OpenGroupCreateForm, self).__init__(*args, **kwargs)
		self.fields['topic'].widget.attrs['style'] = 'width:98%;height:100px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'
		self.fields['rules'].widget.attrs['style'] = 'width:98%;height:250px;border-radius:8px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_topic(self):
		# is_mob_verified, user_score, is_rejoining = self.is_mob_verified, self.score, self.rejoin
		is_mob_verified, is_rejoining = self.is_mob_verified, self.rejoin
		# if (is_mob_verified and user_score >= PUBLIC_GROUP_COST) or (is_mob_verified and is_rejoining):
		if (is_mob_verified) or (is_mob_verified and is_rejoining):
			topic = self.cleaned_data.get("topic")
			topic = topic.strip()
			process_group_topic(topic, topic_len_threshold=PUBLIC_GROUP_MAX_TITLE_SIZE)# no need to send over user_id or unique_id (the latter doesn't even exist)
			return string.capwords(topic)
		# elif user_score < PUBLIC_GROUP_COST:
		#     raise forms.ValidationError('Ye mehfil {0} points se banti hai, apka score {1} hai'.format(PUBLIC_GROUP_COST,user_score))
		else:
			raise forms.ValidationError('Account verify kiye beghair public mehfil nahi banti')

	def clean_rules(self):
		# is_mob_verified, user_score, is_rejoining = self.is_mob_verified, self.score, self.rejoin
		is_mob_verified, is_rejoining = self.is_mob_verified, self.rejoin
		# if (is_mob_verified and user_score >= PUBLIC_GROUP_COST) or (is_mob_verified and is_rejoining):
		if (is_mob_verified) or (is_mob_verified and is_rejoining):
			rules = self.cleaned_data.get("rules")
			rules = rules.strip()
			process_group_rules(rules, rules_len_threshold=PUBLIC_GROUP_MAX_RULES_SIZE)
			return number_new_lines(rules), rules
		# elif user_score < PUBLIC_GROUP_COST:
		#     raise forms.ValidationError('Ye mehfil {0} points se banti hai, apka score {1} hai'.format(PUBLIC_GROUP_COST,user_score))
		else:
			raise forms.ValidationError('Account verify kiye beghair public mehfil nahi banti')

class GroupFeedbackForm(forms.Form):
	"""
	Handles kick feedback validation
	"""
	feedback = forms.CharField(widget=forms.Textarea(attrs={'cols':40,'rows':3,'class': 'cxl','autocomplete': 'off','autofocus': 'autofocus',\
		'autocorrect':'off','autocapitalize':'off','spellcheck':'false','maxlength':GROUP_FEEDBACK_SIZE}),\
	error_messages={'invalid':"Sahi se likhein",'required':"Isey khali nahi chorein"})


	def __init__(self,*args,**kwargs):
		super(GroupFeedbackForm, self).__init__(*args,**kwargs)
		self.fields['feedback'].widget.attrs['style'] = 'width:99%;height:110px;border-radius:10px;border: 1px #E7ECEE solid; background-color:#FAFAFA;padding:5px;'

	def clean_feedback(self):
		feedback = self.cleaned_data.get("feedback").strip()
		feedback_len = len(feedback)
		if feedback_len > GROUP_FEEDBACK_SIZE:
			raise forms.ValidationError('Ye {0} characters se bara nahi likh saktey'.format(GROUP_FEEDBACK_SIZE))
		elif feedback_len < 1:
			raise forms.ValidationError('Isey khali nahi chorein')
		elif feedback_len < 6:
			raise forms.ValidationError('Ye itna chota nahi ho sakta')
		return clear_zalgo_text(feedback)


class GroupPriceOfferForm(forms.Form):
	"""
	Handles price offered to public mehfil owner
	"""
	price = forms.CharField(error_messages={'invalid':"Sirf number likhein",'required':"Isey khali nahi chorein"})

	def __init__(self,*args,**kwargs):
		self.user_id = kwargs.pop('user_id',None)
		self.user_uname = kwargs.pop('user_uname',None)
		self.time_now = kwargs.pop('time_now',None)
		self.score = kwargs.pop('score',None)
		self.group_id = kwargs.pop('group_id',None)
		self.group_owner_id = kwargs.pop('group_owner_id',None)
		self.is_mob_verified = kwargs.pop('is_mob_verified',None)
		super(GroupPriceOfferForm, self).__init__(*args,**kwargs)
		self.fields['price'].widget.attrs['style'] = 'text-align:center;width:115px;height:25px;border-radius:6px;border: 1px #E4E6E8 solid; background-color:#FAFAFA;padding:5px;'
		self.fields['price'].widget.attrs['class'] = 'cxl sp'
		self.fields['price'].widget.attrs['maxlength'] = 4
		self.fields['price'].widget.attrs['autocomplete'] = 'off'
		self.fields['price'].widget.attrs['autocorrect'] = 'off'
		self.fields['price'].widget.attrs['autocapitalize'] = 'off'
		self.fields['price'].widget.attrs['spellcheck'] = 'false'

	def clean_price(self):
		"""
		Go through all the disallowed scenarios one-by-one
		"""
		price, own_id, own_uname, time_now, score, group_id, group_owner_id, is_mob_verified = self.cleaned_data["price"], self.user_id, self.user_uname, \
		self.time_now, self.score, self.group_id, self.group_owner_id, self.is_mob_verified
		is_public = False if retrieve_group_privacy(group_id) == '1' else True
		if is_public and not is_mob_verified:
			# user's not verified their mobile number
			raise forms.ValidationError("Sorry! Mehfil ki ownership sirf verified users ko mil sakti hai")
		elif group_owner_id == str(own_id):
			# already group owner
			raise forms.ValidationError("Ap already is mehfil ke owner hain")
		else:
			try:
				price = int(price)
			except (ValueError, TypeError):
				raise forms.ValidationError("Sirf number likhein")
			if price > score:
				raise forms.ValidationError('Sorry! Ap ne {} points offer kiye, lekin apka score sirf {} points hai'.format(price,score))
			elif is_public and price < PUBLIC_GROUP_MIN_SELLING_PRICE:
				raise forms.ValidationError('Sorry! Offer kam az kam {} points honi chahiye'.format(int(PUBLIC_GROUP_MIN_SELLING_PRICE)))
			elif is_public and price > PUBLIC_GROUP_MAX_SELLING_PRICE:
				raise forms.ValidationError('Sorry! Offer {} points se ziyada nahi honi chahiye'.format(int(PUBLIC_GROUP_MAX_SELLING_PRICE)))
			else:
				try:
					join_date = User.objects.only('date_joined').get(id=own_id).date_joined
				except User.DoesNotExist:
					# this user does not exist thus data incomplete
					raise forms.ValidationError("Sorry! Apki tashkhees nahi ho saki")
				young_age_ttl = (USER_AGE_AFTER_WHICH_PUBLIC_MEHFIL_CAN_BE_CREATED - (time_now - convert_to_epoch(join_date)))
				user_is_freshman = True if young_age_ttl > 0 else False
				if user_is_freshman: 
					# user too young to own a public mehfil - old users' "young_age_ttl" statistic would be highly negative
					raise forms.ValidationError("Sorry! Ap ye {} tak nahi kar saktey kiyunke apko Damadam join kiye ziyada time nahi guzra".\
						format(human_readable_time(young_age_ttl)))
				elif time_now - retrieve_group_creation_time(group_id) < GROUP_AGE_AFTER_WHICH_IT_CAN_BE_TRANSFERRED:
					# mehfil too young to be transferred (i.e. less than 10 days old)
					raise forms.ValidationError("Sorry! Is mehfil ko create huay itna time nahi guzra ke ownership transfer ki ja sakey")
				elif is_public and retrieve_group_category(group_id) == '2' and own_uname not in FEMALES:
					raise forms.ValidationError("Sorry! Is mehfil ki ownership sirf pink stars ke liya hai")
				else:
					data = is_group_member_and_rules_signatory(group_id, own_id)
					is_mem, is_sig = data[0], data[1]
					if is_mem and not is_sig:
						raise forms.ValidationError("Sorry! Ap ye nahi kar saktey kiyun ke ap ne mehfil ke rules nahi accept kiye huay")
					elif not is_mem:
						raise forms.ValidationError("Sorry! Ap ye nahi kar saktey kiyun ke ap mehfil ke member nahi")
					else:
						user_ttl, ttl_type = group_ownership_transfer_blocked_by_rate_limit(group_id, group_owner_id, own_id)
						if user_ttl:
							if ttl_type == 'owner':
								# cannot proceed since mehfil owner is rate-limited (and can't accept your request)
								raise forms.ValidationError("Sorry! Ye owner {} tak aisi koi offer receive nahi kar sakta kiyunke is ne recently mehfil ka lain dain kiya hai".format(human_readable_time(user_ttl)))
							else:
								# cannot proceed since you are rate-limited (and can't send your request)
								raise forms.ValidationError("Sorry! Ap {} tak aisi koi request send nahi kar saktey kiyunke ap ne recently mehfil ka lain dain kiya hai".format(human_readable_time(user_ttl)))		
						else:
							ttl = ownership_request_rate_limit(group_id, own_id)
							if ttl:
								# the user already sent a transfer request, and must wait for a week before doing so again
								raise forms.ValidationError("Sorry! Ap is mehfil owner ko dubara ownership transfer ki request {} tak send nahi kar saktey".format(human_readable_time(ttl)))
							else:
								return price


class OfficerApplicationForm(forms.Form):
	"""
	Handles submission of 'officer' application by a user (to a public mehfil owner)
	"""
	answer1 = forms.CharField(required=True,widget=forms.Textarea(attrs={'autofocus': 'autofocus','autocomplete': 'off',\
		'class': 'cxl sp', 'autocapitalize':'off','spellcheck':'false','autocorrect':'off',\
		'maxlength':PUBLIC_GROUP_OFFICER_APPLICATION_ANSWER_LEN}),error_messages={'required': 'Ye likhna zaruri hai'})
	answer2 = forms.CharField(required=True,widget=forms.Textarea(attrs={'class': 'cxl sp','autocomplete': 'off',\
		'autocapitalize':'off','spellcheck':'false','autocorrect':'off','maxlength':PUBLIC_GROUP_OFFICER_APPLICATION_ANSWER_LEN}),\
	error_messages={'required': 'Ye likhna zaruri hai'})

	def __init__(self,*args,**kwargs):
		super(OfficerApplicationForm, self).__init__(*args,**kwargs)
		self.fields['answer1'].widget.attrs['style'] = 'text-align:left;width:95%;height:130px;border-radius:6px;border: 1px #E4E6E8 solid; background-color:#FAFAFA;padding:5px;'
		self.fields['answer2'].widget.attrs['style'] = 'text-align:left;width:95%;height:130px;border-radius:6px;border: 1px #E4E6E8 solid; background-color:#FAFAFA;padding:5px;'

	def clean_answer1(self):
		answer1 = self.cleaned_data["answer1"]
		len_answer1 = len(answer1)
		if len_answer1 < 12:
			raise ValidationError("Itna chota answer nahi likh saktey")
		elif len_answer1 > PUBLIC_GROUP_OFFICER_APPLICATION_ANSWER_LEN:
			raise ValidationError("Itna lamba answer nahi likh saktey")
		return answer1

	def clean_answer2(self):
		answer2 = self.cleaned_data["answer2"]
		len_answer2 = len(answer2)
		if len_answer2 < 5:
			raise ValidationError("Itna chota answer nahi likh saktey")
		elif len_answer2 > PUBLIC_GROUP_OFFICER_APPLICATION_ANSWER_LEN:
			raise ValidationError("Itna lamba answer nahi likh saktey")
		return answer2


class GroupTypeForm(forms.Form):
	class Meta:
		pass


class ClosedGroupHelpForm(forms.Form):
	class Meta:
		pass		


class ReinviteForm(forms.Form):
	class Meta:
		pass


class ReinvitePrivateForm(forms.Form):
	class Meta:
		pass


# class GroupPageForm(forms.Form):
# 	class Meta:
# 		model = Reply


class DirectMessageCreateForm(forms.Form):
	class Meta:
		pass
		# model = Group

class DirectMessageForm(forms.Form):
	class Meta:
		pass