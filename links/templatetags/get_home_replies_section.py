from django import template

register = template.Library()

@register.inclusion_tag(file_name='home_replies_section.html')
def home_replies_section(raw_replies):
	replies = []
	raw_reply_set = filter(None,raw_replies.split('#el#'))
	counter = 0
	for raw_reply in reversed(raw_reply_set):
		components = raw_reply.split("#",3)
		reply_head, epoch_time, text = components[0], components[1], components[2]
		reply = {}
		reply["reply_head"] = reply_head
		reply["text"] = text
		reply["epoch_time"] = float(epoch_time)
		replies.append(reply)
		counter += 1
		if counter > 5:
			# this ensure only 6 replies can show up on home (at max)
			break
	return {'replies':replies}