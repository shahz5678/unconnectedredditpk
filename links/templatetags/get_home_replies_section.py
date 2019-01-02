from django import template

register = template.Library()

@register.inclusion_tag(file_name='home_replies_section.html')
def home_replies_section(raw_replies, static_url, self_user_id, score, home_hash):
	replies = []
	raw_reply_set = filter(None,raw_replies.split('#el#'))
	if raw_reply_set:
		counter = 0
		for raw_reply in reversed(raw_reply_set):
			if raw_reply[0] != '#':# exception handling
				components = raw_reply.split("#",5)
				reply = {}
				reply["is_pinkstar"], reply["epoch_time"], reply["replier_id"], reply['replier_username'], reply["link_id"], reply["text"]  = components[0], \
				components[1], components[2], components[3], components[4], components[5]
				replies.append(reply)
			counter += 1
			if counter > 5:
				# this ensures only 6 replies can show up on home (at max)
				break
		return {'replies':replies,'static_url':static_url,'self_user_id':self_user_id, 'score':score, 'possible':True,'home_hash':home_hash}
	else:
		return {'possible':False}