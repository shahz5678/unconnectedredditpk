from links.ecomm import x2lite_details, x32_details, buyer_loc, process_city, post_basic_item, post_seller_info, \
post_basic_item_photos, init_classified, approve_classifieds #add_shop, shops_by_city, show_shop_choices, ecomm_welcome
from links.number_verification import verify_basic_item_seller_number
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required as auth
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	url(r'^classified_approval_dashboard/$', auth(approve_classifieds),name='approve_classifieds'),
	#############################################E Commerce##########################################
	url(r'^item_ki_detail_likho/$', auth(post_basic_item),name='post_basic_item'),
	url(r'^baichney_waley_ki_detail_likho/$', auth(post_seller_info),name='post_seller_info'),
	url(r'^item_ki_pics_lagao/$', auth(post_basic_item_photos),name='post_basic_item_photos'),
	url(r'^kuch_baicho/$', auth(init_classified),name='init_classified'),
	# url(r'^baichnay_ka_tareeqa/$', auth(),name=''),
	url(r'^vsn/$',verify_basic_item_seller_number, name="verify_basic_item_seller_number"),
	############################################################
	# url(r'^shop_city/(?P<city>[\w.@+-]+)/$', auth(shops_by_city),name='shops_by_city'),
	# url(r'^add_shop/$', auth(add_shop),name='add_shop'),
	# url(r'^mobile/$', auth(show_shop_choices),name='ecomm'),

	# url(r'^mobile/x32/$', x32_details,name='x32'),
	# url(r'^mobile/x2lite/$', x2lite_details,name='x2lite'),
	# url(r'^mobile/loc/$', auth(buyer_loc),name='buyer_loc'),
	# url(r'^mobile/proc_city/$', auth(process_city),name='process_city'),
)