# coding=utf-8
from django import forms
from django.core.exceptions import ValidationError
from forms import strip_zero_width_characters, repetition_found
from redis9 import direct_response_exists, retrieve_prev_replier_rate, impose_reply_rate_limit, is_rate_limited
from links.templatetags import future_time
from redis6 import human_readable_time
from score import MAX_HOME_REPLY_SIZE
from tasks import log_reply_rate
from redis4 import is_limited


def prescribe_direct_response_rate_limit(typing_speed_1, text_1_len, typing_speed_2=None, text_2_len=None, typing_speed_3=None, text_3_len=None):
	"""
	Determines whether the rate of typing exceeds benchmarks of 'flooding'
	"""
	is_over_speeding = False
	if typing_speed_1 and typing_speed_2 and typing_speed_3:
		
		avg_typing_speed = (typing_speed_1+typing_speed_2+typing_speed_3)/3.0
		##################################
		# this user is writing short stuff - take that into account when judging the rate limit
		if text_1_len < 4 and text_2_len < 4 and text_3_len < 4:
			if avg_typing_speed > 2.58:
				# rate-limit this person
				is_over_speeding = True
		##################################
		elif typing_speed_1 > 5 and avg_typing_speed > 5.5:
			# rate-limit this person
			is_over_speeding = True

	elif typing_speed_1 and typing_speed_2:

		avg_typing_speed = (typing_speed_1+typing_speed_2)/2.0
		##################################
		# this user is writing short stuff - take that into account when judging the rate limit
		if text_1_len < 4 and text_2_len < 4:
			if avg_typing_speed > 3.68:
				# rate-limit this person
				is_over_speeding = True
		##################################
		elif typing_speed_1 > 5 and avg_typing_speed > 6.5:
			# rate-limit this person
			is_over_speeding = True

	elif typing_speed_1:
		if text_1_len < 4:
			if typing_speed_1 > 4:
				# rate-limit this person
				is_over_speeding = True
		##################################
		# elif typing_speed_1 > 8:
		# 	# rate-limit this person
		# 	is_over_speeding = True

	return is_over_speeding



def determine_direct_response_rate(reply_len, replier_id, time_now):
	"""
	Determines whether a replier is writing too fast (and needs to be slowed down)
	"""
	
	# first check if user is already rate-limited
	rate_limited, time_length = is_rate_limited(replier_id)
	if rate_limited:
		return rate_limited, time_length
	# since no rate-limited, now check if user ought to be rate-limited
	else:
		is_over_speeding = False
		recent_reply_lens_and_times = retrieve_prev_replier_rate(replier_id)

		if recent_reply_lens_and_times:
			# generate up to prev 3 typing speeds
			# provide validation error if reply rates have exceeded acceptable thresholds
			len_data = len(recent_reply_lens_and_times)

			if len_data == 1:
				text_2_time = float(recent_reply_lens_and_times[0].partition(":")[-1])
				latest_typing_speed = (1.0*reply_len/(time_now-text_2_time))
				is_over_speeding = prescribe_direct_response_rate_limit(typing_speed_1=latest_typing_speed, text_1_len=reply_len)
			
			if len_data == 2:
				data_2 = recent_reply_lens_and_times[0].partition(":")
				text_2_len, text_2_time = float(data_2[0]), float(data_2[-1])
				data_3 = recent_reply_lens_and_times[1].partition(":")
				text_3_len, text_3_time = float(data_3[0]), float(data_3[-1])

				latest_typing_speed = (1.0*reply_len/(time_now-text_2_time))
				denom_2 = text_2_time-text_3_time
				previous_typing_speed = (text_2_len/denom_2) if denom_2 > 0 else 100# give it a huge value
				is_over_speeding = prescribe_direct_response_rate_limit(typing_speed_1=latest_typing_speed,text_1_len=reply_len,\
					typing_speed_2=previous_typing_speed, text_2_len=text_2_len)

			elif len_data >= 3:
				data_2 = recent_reply_lens_and_times[0].partition(":")
				text_2_len, text_2_time = float(data_2[0]), float(data_2[-1])
				data_3 = recent_reply_lens_and_times[1].partition(":")
				text_3_len, text_3_time = float(data_3[0]), float(data_3[-1])
				text_4_time = float(recent_reply_lens_and_times[2].partition(":")[-1])

				latest_typing_speed = (1.0*reply_len/(time_now-text_2_time))
				denom_2 = text_2_time-text_3_time
				previous_typing_speed = text_2_len/denom_2 if denom_2 > 0 else 100# give it a huge value
				denom_3 = text_3_time-text_4_time
				last_typing_speed = text_3_len/denom_3 if denom_3 > 0 else 100# give it a huge value

				is_over_speeding = prescribe_direct_response_rate_limit(typing_speed_1=latest_typing_speed,text_1_len=reply_len,\
					typing_speed_2=previous_typing_speed, text_2_len=text_2_len, typing_speed_3=last_typing_speed, text_3_len=text_3_len)

			else:
				# do nothing
				pass

		return is_over_speeding, None


#################################################

class DirectResponseForm(forms.Form):
	"""
	Handles 'direct response' functionality for reply objs of type '3' (text post), '4' (image post), '5' (pub meh), '6' (prv meh), '7' (1-on-1)
	"""
	single_response = forms.BooleanField(required=False, initial=False)


	def __init__(self,*args,**kwargs):
		self.render_page_with_one_response = kwargs.pop('render_page_with_one_response',None)
		self.thin_strip = kwargs.pop('thin_strip',None)
		self.with_id = kwargs.pop('with_id',None)
		self.obj_type = kwargs.pop('obj_type',None)
		self.parent_obj_id = kwargs.pop('parent_obj_id',None)
		self.sender_id = kwargs.pop('sender_id',None)
		self.receiver_id = kwargs.pop('receiver_id',None)
		self.time_now = kwargs.pop('time_now',None)
		super(DirectResponseForm, self).__init__(*args,**kwargs)
		if self.thin_strip:
			# initializing a default, 'thin' Charfield for inline usage
			self.fields['direct_response'] = forms.CharField(error_messages={'invalid': "Reply sahi likhein",'required':"Reply likhna zaruri hai"})
			self.fields['direct_response'].widget.attrs['placeholder'] = 'Reply likhein..'
			self.fields['direct_response'].widget.attrs['maxlength'] = MAX_HOME_REPLY_SIZE
			self.fields['direct_response'].widget.attrs['class'] = 'box-with-button-right sp'
			self.fields['direct_response'].widget.attrs['style'] = 'border: 1px solid lightgrey; border-radius:4px;'
		else:
			# initializing a Textarea for regular usage (as a text box)
			self.fields['direct_response'] = forms.CharField(widget=forms.Textarea(attrs={'cols': 30,'autocomplete': 'off',\
				'placeholder':'Reply likhein..','maxlength':MAX_HOME_REPLY_SIZE}),\
			error_messages={'invalid': "Reply sahi likhein",'required':"Reply likhna zaruri hai"})
			if self.render_page_with_one_response:
				self.fields['direct_response'].widget.attrs['style'] = 'width:100%;height:100px;border-radius:0;border:none; background-color:#ecfffb;padding:10px;box-sizing:border-box'
				self.fields['direct_response'].widget.attrs['class'] = 'cxl sp lsp'
				self.fields['direct_response'].widget.attrs['autofocus'] = 'autofocus'
			else:
				self.fields['direct_response'].widget.attrs['style'] = 'width:100%;height:65px;border-radius:0;border:none; background-color:#ecfffb;padding:10px;box-sizing:border-box'
				self.fields['direct_response'].widget.attrs['class'] = 'cl sp lsp'
			if self.with_id:
				self.fields['direct_response'].widget.attrs['id'] = 'dir_rep_body'
		self.fields['direct_response'].widget.attrs['autocomplete'] = 'off'
		self.fields['direct_response'].widget.attrs['autocapitalize'] = 'off'
		self.fields['direct_response'].widget.attrs['spellcheck'] = 'false'

	def clean_direct_response(self):
		"""
		Ensure the direct reply is valid
		"""
		direct_response, obj_type, parent_obj_id, sender_id, receiver_id = self.cleaned_data["direct_response"].strip(), self.obj_type, \
		self.parent_obj_id, self.sender_id, self.receiver_id
		
		# NOTE: receiver_id is own_id, sender_id is target_id (for the purposes of this function)

		##########################################################
		if parent_obj_id and sender_id and receiver_id and obj_type in ('3','4','5','6','7'):
			direct_response = strip_zero_width_characters(direct_response)
			if not direct_response or direct_response.isspace():
				raise forms.ValidationError('Reply likhna zaruri hai')
			len_reply = len(direct_response)
			if len_reply > MAX_HOME_REPLY_SIZE:
				raise forms.ValidationError('Reply {} chars se lamba nahi likhein, ap ne {} chars likhe'.format(MAX_HOME_REPLY_SIZE, len_reply))
			##########################################################
			# only applicable to replies under posts
			if obj_type in ('3','4'):

				is_over_speeding, rate_limited_for = determine_direct_response_rate(reply_len=len_reply, replier_id=receiver_id, \
					time_now=self.time_now)

				if is_over_speeding:
					if rate_limited_for:
						log_reply_rate.delay(replier_id=receiver_id, text=direct_response, time_now=self.time_now, reply_target=sender_id, \
							marked_fast='1' if is_over_speeding else '0', rate_limited='1')
					else:
						rate_limited, time_length = impose_reply_rate_limit(replier_id=receiver_id)
						if rate_limited:
							log_reply_rate.delay(replier_id=receiver_id, text=direct_response, time_now=self.time_now, reply_target=sender_id, \
								marked_fast='1' if is_over_speeding else '0', rate_limited='1')
						else:
							log_reply_rate.delay(replier_id=receiver_id, text=direct_response, time_now=self.time_now, reply_target=sender_id, \
								marked_fast='1' if is_over_speeding else '0', rate_limited='0')
				else:
					log_reply_rate.delay(replier_id=receiver_id, text=direct_response, time_now=self.time_now, reply_target=sender_id, \
							marked_fast='1' if is_over_speeding else '0', rate_limited='0')



				# # this person is already rate limited
				# if rate_limited_for:
				# 	raise forms.ValidationError('Andha dhund replies likhney ki wajah se ap dubara reply kar sakein ge {}'.format(future_time.future_time(rate_limited_for)))		
				
				# # check whether this person ought to be rate limited
				# elif is_over_speeding:
				# 	rate_limited, time_length = impose_reply_rate_limit(replier_id=receiver_id)
				# 	if rate_limited:
				# 		raise forms.ValidationError('Andha dhund replies likhney ki wajah se ap dubara reply kar sakein ge {}'.format(future_time.future_time(time_length)))

			##########################################################
			# only applicable to mehfils
			elif obj_type in ('5','6'):
				section = 'pub_grp' if obj_type == '5' else 'prv_grp'
 				if repetition_found(section=section,section_id=parent_obj_id,user_id=receiver_id, target_text=direct_response):
					raise forms.ValidationError('Milti julti baatien nahi likhein')
				else:
					rate_limited, reason = is_limited(receiver_id,section=section,with_reason=True)
					if rate_limited > 0:
						raise forms.ValidationError('Ap mehfil mein likhne se {0} tak banned ho. Reason: {1}'.\
							format(human_readable_time(rate_limited),reason))
			##########################################################

			exists, hide_status = direct_response_exists(obj_type=obj_type, parent_obj_id=parent_obj_id, sender_id=sender_id, \
				receiver_id=receiver_id, with_hide_status=True)
			if exists:
				return direct_response, hide_status
			else:
				return direct_response, False
		else:
			raise forms.ValidationError('Phir se koshish karein')