from django import template

register = template.Library()

@register.inclusion_tag(file_name='device.html')
def device(submission_device, static_url):
	# return {'page':page_obj}
	return {'submission_device':submission_device,'static_url':static_url}
	# if submission_device == '1':
	# 	return 'featurephone.png'
	# elif submission_device == '2':
	# 	return 'smartphone.png'
	# elif submission_device == '3':
	# 	return 'laptop.png'
	# elif submission_device == '4':
	# 	return 'tablet.png'
	# elif submission_device == '5':
	# 	return 'other.png'
	# else:
	# 	return None

	# {% if submission.submission_device == '1' %}
 #        &nbsp;<img src="{{ STATIC_URL }}img/featurephone.png" alt="no pic"></img>
 #        {% elif submission.submission_device == '2' %}
 #        &nbsp;<img src="{{ STATIC_URL }}img/smartphone.png" alt="no pic"></img>
 #        {% elif submission.submission_device == '4' %}
 #        &nbsp;<img src="{{ STATIC_URL }}img/tablet.png" alt="no pic"></img>
 #        {% elif submission.submission_device == '5' %}
 #        &nbsp;<img src="{{ STATIC_URL }}img/other.png" alt="no pic"></img>
 #        {% elif submission.submission_device == '3' %}
 #        &nbsp;<img src="{{ STATIC_URL }}img/laptop.png" alt="no pic"></img>
 #        {% else %}
 #        {% endif %}
