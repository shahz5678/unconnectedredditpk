import requests
from optimizely import optimizely
from optimizely.event_dispatcher import EventDispatcher as event_dispatcher
# from optimizely.logger import SimpleLogger as logger

class OptimizelyConfigManager(object):
  obj = None

  def __init__(self, project_id):
    self.project_id = project_id

  def get_obj(self):
    if not self.obj:
      self.set_obj()
    return self.obj

  def set_obj(self, url=None):
    if not url:
      url = 'https://cdn.optimizely.com/json/{0}.json'.format(self.project_id)

    datafile = self.retrieve_datafile(url)
    self.obj = optimizely.Optimizely(datafile,skip_json_validation=True,event_dispatcher=event_dispatcher)#,logger=logger())

  def retrieve_datafile(self, url):
    datafile = requests.get(url).text
    # print datafile
    return datafile