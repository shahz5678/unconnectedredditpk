#full documentation at: http://nodotcom.org/python-facebook-tutorial.html

import facebook, os

def photo_poster(image_obj=None, caption=None):
  # Fill in the values noted in documentation here:

  PAGE_ID = '1812492382364506'#os.environ.get('FACEBOOK_PAGE_ID')
  ACCESS_TOKEN = 'EAAQWkmy1MFYBAF4kDKRuQ8fjj2ocphX9vzijqY0SFbT5IfmRG9bvzfyamBMVGllsABmXORILAPH9qmYojcTNpZBHM8wx2ZCxOFMdOuZCRgOuqYixCrsVgbD4bhFoa8yxMGwISqPOBZAqviGQlcZB7induz6m8ZAfcZD'#os.environ.get('FACEBOOK_ACCESS_TOKEN')

  cfg = {
    "page_id"      : PAGE_ID,  # Step 1
    "access_token" : ACCESS_TOKEN   # Step 3
    }
  caption = caption+" (https://damadam.pk)"
  # print cfg
  api = get_api(cfg)
  status = api.put_photo(image=(image_obj),message=caption)
  # print "status: %s" % status

def get_api(cfg):
  graph = facebook.GraphAPI(cfg['access_token'])
  # print "graph: %s" % graph
  # Get page token to post as the page. You can skip 
  # the following if you want to post as yourself. 
  resp = graph.get_object('me/accounts')
  # resp = graph.get_object('10154886323073885/accounts')
  # print "getting own account: %s" % resp
  page_access_token = None
  for page in resp['data']:
    if page['id'] == cfg['page_id']:
      page_access_token = page['access_token']
  graph = facebook.GraphAPI(page_access_token)
  return graph 
  # You can also skip the above if you get a page token:
  # http://stackoverflow.com/questions/8231877/facebook-access-token-for-pages
  # and make that long-lived token as in Step 3
