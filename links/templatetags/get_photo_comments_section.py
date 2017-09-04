from django import template

register = template.Library()

@register.inclusion_tag(file_name='photo_comments_section.html')
def photo_comments_section(raw_comments, static_url):
	comments = []
	raw_comment_set = filter(None,raw_comments.split('#el#'))
	counter = 0
	for raw_comment in reversed(raw_comment_set):
		components = raw_comment.split("#",3)
		comment = {}
		comment["writer_av_url"], comment["writer_uname"], comment["epoch_time"], comment["text"] = \
		components[0], components[1], float(components[2]), components[3]
		comments.append(comment)
		counter += 1
		if counter > 5:
			# this ensure only 6 comments can show up on the photo page (at max)
			break
	return {'comments':comments, 'static_url':static_url}