from django import template
from links.page_controls import PERSONAL_GROUP_URL_IMG_WIDTH

register = template.Library()

@register.filter(name='url_img_height')
def url_img_height(hw_ratio):
	if hw_ratio:
		try:
			hw_ratio = float(hw_ratio)
			if hw_ratio > 2.5:
				# the image is too tall
				return int(PERSONAL_GROUP_URL_IMG_WIDTH*2.5)
			else:
				return int(PERSONAL_GROUP_URL_IMG_WIDTH*hw_ratio)
		except (ValueError,TypeError):
			return PERSONAL_GROUP_URL_IMG_WIDTH
	else:
		return ''