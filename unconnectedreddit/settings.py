# Django settings for unconnectedreddit project.
import os
from datetime import datetime, timedelta
from env import ON_AZURE, DB_PASSWORD, MIXPANEL_TOKEN, AWS_STORAGE_BUCKET

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #i.e. to /unconnectedredditpk/unconnectedreddit/ 'project' folder
MAIN_DIR = os.path.dirname(os.path.dirname(__file__)) #i.e. to /unconnectedredditpk/ external folder

ON_MAC = os.environ.get('ON_MAC')
MAC_USER = os.environ.get('MAC_USER')
RATELIMIT_CACHE_BACKEND = 'links.mybrake.MyBrake'

#git init
#git remote add origin https://github.com/mhb11/unconnectedredditpk.git
#git pull origin master
#git add <files>
#git push origin master	

expires = datetime.utcnow() + timedelta(days=365)
expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

S3_STORAGE_CLASS = 'links.imagestorage.S3Storage'
AWS_HEADERS = {'Expires': expires,'Cache-Control': 'max-age=31536000'}
AWS_STORAGE_BUCKET_NAME = AWS_STORAGE_BUCKET
AWS_QUERYSTRING_AUTH = False


if ON_AZURE == '1':
	DEBUG=False
	# STATIC_URL = '//damadamstatic.azureedge.net/'
else:
	DEBUG=True
	
STATIC_URL = '/static/'

TEMPLATE_DEBUG = DEBUG

ADMINS = (
	('H B', 'baig.hassan@gmail.com'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']																																														

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'UTC'#'Asia/Oral'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-68289796-1'

GOOGLE_ANALYTICS = {
	'google_analytics_id': 'UA-121366807-1',
}


GOOGLE_ANALYTICS_SITE_SPEED = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''
FONTS_ROOT = os.path.join(BASE_DIR, 'fonts/')
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''
FONTS_URL = '/fonts/'
# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = 'staticfiles'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
# STATIC_URL = '/static/'
# STATIC_URL = '//damadamstatic.azureedge.net/'

# Additional locations of static files
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'iapysen!%y-wvpfdmlp^!*@#nkn3hi_y9(%si)5c(tig_r29a6'

# List of callables that know how to import templates from various sources.

if ON_AZURE == '1':
	TEMPLATE_LOADERS = (
		('django.template.loaders.cached.Loader', (
			'django.template.loaders.filesystem.Loader',
			'django.template.loaders.app_directories.Loader',
		)),
	)
else:
	TEMPLATE_LOADERS = (
		'django.template.loaders.filesystem.Loader',
		'django.template.loaders.app_directories.Loader',
	)

MIDDLEWARE_CLASSES = (
	# 'unconnectedreddit.middleware.NoWWWRedirect.NoWWWRedirectMiddleware',
 #   'debug_toolbar.middleware.DebugToolbarMiddleware',
	'unconnectedreddit.middleware.XForwardedFor.XForwardedForMiddleware',
	'user_sessions.middleware.SessionMiddleware',
	# 'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	#'django.contrib.auth.middleware.SessionAuthenticationMiddleware', #does not exist in django 1.5
	'unconnectedreddit.middleware.MobileVerified.MobVerifiedMiddleware',
	'unconnectedreddit.middleware.WhoseOnline.WhoseOnlineMiddleware', #enable from here
	'unconnectedreddit.middleware.EcommTracking.TrackUniqueEcommVisitsMiddleware',
	'unconnectedreddit.middleware.HellBanned.HellBannedMiddleware',
	#'request.middleware.RequestMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'mobileesp.middleware.MobileDetectionMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE = 'user_sessions.backends.db'
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

#MOBI_DETECT_TABLET = True
#MOBI_USER_AGENT_IGNORE_LIST = ['ipad', 'android', 'iphone',]

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.csrf",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.contrib.messages.context_processors.messages",
	"django.core.context_processors.request",
	"django.core.context_processors.tz",
	)

ROOT_URLCONF = 'unconnectedreddit.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'unconnectedreddit.wsgi.application'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	# 'django.contrib.sessions',
	'user_sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.comments',
	'links',
	'unconnectedreddit',
	'south',
	#'registration', #found at has@has-VirtualBox:~/.virtualenvs/unconnectedreddit/local/lib/python2.7/site-packages/registration/backends/simple$
	'bootstrap_pagination',
	'djcelery',
	'tweepy',
	'django.contrib.humanize',
	'analytical',
	'mathfilters',
	'storages',
	'emoticons',
	'django_extensions',
	#'google_analytics',
	#'request',
	# 'debug_toolbar',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
)

if ON_MAC == '1':
	CACHES = {
		'default': {
			'BACKEND':'django.core.cache.backends.memcached.MemcachedCache',
			'LOCATION':'unix:usr/local/var/run/memcached/memcached.sock',
			# 'LOCATION':'127.0.0.1:11211',
		}
	}
else:
	CACHES = {
		'default': {
			'BACKEND':'django.core.cache.backends.memcached.MemcachedCache',
			'LOCATION':'unix:/var/run/memcached/memcached.sock',
			# 'LOCATION':'127.0.0.1:11211',
		}
	}

CSRF_FAILURE_VIEW = 'links.views.csrf_failure'

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/2",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient"
#         },
#         "KEY_PREFIX": "example"
#     }
# }

from django.core.urlresolvers import reverse_lazy

LOGIN_URL=reverse_lazy('login')
LOGIN_REDIRECT_URL = reverse_lazy('home')
LOGOUT_URL=reverse_lazy('logout')

# A sample error logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		}
	},
	'loggers': {
		'django.request': {
			'handlers': ['mail_admins'],
			'level': 'ERROR',
			'propagate': True,
		},
	}
}

import dj_database_url
if ON_AZURE == '1':
	# DATABASE_URL = 'postgres://<username>:<password>@40.114.247.165:5432/myapp'
	# DATABASES = {
	# 'default': dj_database_url.config(default=DATABASE_URL)
	# }
	DEFAULT_FILE_STORAGE = S3_STORAGE_CLASS
	DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'damadam',                      # Or path to database file if using sqlite3.
		'USER': 'ubuntu',
		'PASSWORD': DB_PASSWORD,
		'HOST': '/var/run/postgresql',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
		'PORT': '6432',
	}
}
elif ON_MAC == '1':
	# Parse database configuration from $DATABASE_URL
	DEFAULT_FILE_STORAGE = S3_STORAGE_CLASS
	DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'damadampakistan',                      # Or path to database file if using sqlite3.
		# The following settings are not used with sqlite3:
		'USER': MAC_USER,
		'PASSWORD': DB_PASSWORD,
		'HOST': '',
		'PORT': '5432',
	}
}
else:
	# Parse database configuration from $DATABASE_URL
	DEFAULT_FILE_STORAGE = S3_STORAGE_CLASS#'storages.backends.azure_storage.AzureStorage'
	DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'damadampakistan',                      # Or path to database file if using sqlite3.
		# The following settings are not used with sqlite3:
		'USER': 'hassan',
		'PASSWORD': DB_PASSWORD,
		'HOST': '/var/run/postgresql',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
		'PORT': '6432',                      # Set to empty string for default.
	}
}

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

import djcelery
djcelery.setup_loader()
# config settings for Celery Daemon

# Redis broker
if ON_MAC == '1':
	BROKER_URL = 'redis+socket:///usr/local/var/run/redis/redis.sock'
elif ON_AZURE == '1':
	BROKER_URL = 'redis+socket:///var/run/redis.sock'
else:
	BROKER_URL = 'redis+socket:///var/run/redis/redis.sock'

BROKER_TRANSPORT = 'redis'

# List of modules to import when celery starts, in myapp.tasks form. 
CELERY_IMPORTS = ('links.tasks', )  

CELERY_ALWAYS_EAGER = False

#The backend is the resource which returns the results of a completed task from Celery. 6379 is the default port to the redis server.
if ON_MAC == '1':
	CELERY_RESULT_BACKEND = 'redis+socket:///usr/local/var/run/redis/redis.sock'
elif ON_AZURE == '1':
	CELERY_RESULT_BACKEND = 'redis+socket:///var/run/redis.sock'
else:
	CELERY_RESULT_BACKEND = 'redis+socket:///var/run/redis/redis.sock'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IGNORE_RESULT=True

from datetime import timedelta

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

CELERYBEAT_SCHEDULE = {
	'tasks.rank_photos': {
		'task': 'tasks.rank_photos',
		'schedule': timedelta(seconds=120*60), #execute every 12 mins, ranks photos from the feed
	},
	'tasks.trim_whose_online': {
		'task': 'tasks.trim_whose_online',
		'schedule': timedelta(seconds=5*60), #execute every 5 mins, trims online users' list
	},
	'tasks.rank_all_photos': {
		'task': 'tasks.rank_all_photos',
		'schedule': timedelta(seconds=110*60), #execute every 11 mins, spew best photo on Facebook's Fan Page
	},
	'tasks.rank_all_photos1': {
		'task': 'tasks.rank_all_photos1',
		'schedule': timedelta(seconds=60), #execute every 60 seconds, cricket score enqueuing is managed through this
	},
	'tasks.calc_photo_quality_benchmark': {
		'task': 'tasks.calc_photo_quality_benchmark',
		'schedule': timedelta(seconds=86400), # execute every 24 hours, setting top photo uploaders list
	},
	'tasks.calc_ecomm_metrics': {
		'task': 'tasks.calc_ecomm_metrics',
		'schedule': timedelta(seconds=86400), # execute every 24 hours, calculates ecomm metrics
	},
	'tasks.calc_gibberish_punishment': {
		'task': 'tasks.calc_gibberish_punishment',
		'schedule': timedelta(seconds=45*60), # execute every 45 mins, calculates punishment meted out to gibberish writers
	},
	'tasks.sanitize_unused_ecomm_photos': {
		'task': 'tasks.sanitize_unused_ecomm_photos',
		'schedule': timedelta(seconds=15*10*60), # execute every 2.5 hours, deletes unused ecomm photos from the S3 bucket
	},
	'tasks.expire_classifieds': {
		'task': 'tasks.expire_classifieds',
		'schedule': timedelta(seconds=55*60), # execute every 55 mins, processes ad_expiry of ecomm ads
	},
	'tasks.delete_expired_classifieds': {
		'task': 'tasks.delete_expired_classifieds',
		'schedule': timedelta(seconds=2*24*60*60), # execute every 2 days, processes expiry of classified ads
	},
	'tasks.rank_home_posts': {
		'task': 'tasks.rank_home_posts',
		'schedule': timedelta(seconds=5*60), # execute every 5 mins, home post ordering tasks
	},
	'tasks.trim_top_group_rankings': {
		'task': 'tasks.trim_top_group_rankings',
		'schedule': timedelta(seconds=60*60*2), # execute every two hours
	},
	'tasks.whoseonline': {
		'task': 'tasks.whoseonline',
		'schedule': timedelta(seconds=60),  # execute every 60 seconds, calculates who all is online
		'args': (),
	},
	'tasks.fans': {
		'task': 'tasks.fans',
		'schedule': timedelta(seconds=1200),  # execute every 20 mins, displays correct num fans in top photos list
		'args': (),
	},
	'tasks.salat_streaks': {
		'task': 'tasks.salat_streaks',
		'schedule': timedelta(seconds=1200),  # execute every 20 mins, calculates salat streaks for users
		'args': (),
	},
	'tasks.public_group_ranking_clean_up_task': {
		'task': 'tasks.public_group_ranking_clean_up_task',
		'schedule': timedelta(seconds=10*25*60),  # unused task - available for something new
		'args': (),
	},
		'tasks.salat_info': {
		'task': 'tasks.salat_info',
		'schedule': timedelta(seconds=5*60), #execute every 5 mins, calculates which salat is next, which was previous, etc.
	},
	'tasks.delete_exited_personal_group': {
		'task': 'tasks.delete_exited_personal_group',
		'schedule': timedelta(seconds=24*60*60), # execute every 24 hours (hard deletion called on 1-on-1 groups which were exited)
	},
	'tasks.rank_mehfils': {
		'task': 'tasks.rank_mehfils',
		'schedule': timedelta(seconds=24*60*60), # execute every 24 hours (ranks mehfils with highest DAU/Bi-weekly AU)
	},
	'tasks.empty_idle_public_and_private_groups': {
		'task': 'tasks.empty_idle_public_and_private_groups',
		'schedule': timedelta(seconds=2*24*60*60), # execute every 2 days (cleans out the chats in idle public and private mehfils)
	},
	'tasks.delete_chat_from_idle_personal_group': {
		'task': 'tasks.delete_chat_from_idle_personal_group',
		'schedule': timedelta(seconds=3*24*60*60), # execute every 3 days (cleans out the chat in idle 1-on-1 groups)
	},
	'tasks.cleanse_complainers': {
		'task': 'tasks.cleanse_complainers',
		'schedule': timedelta(seconds=3*24*60*60), # execute every 3 days (cleanses content complainers who no longer lodge complaints)
	},
	'tasks.delete_idle_public_and_private_groups': {
		'task': 'tasks.delete_idle_public_and_private_groups',
		'schedule': timedelta(seconds=4*24*60*60), # execute every 4 days (deletes public and private mehfils that have gone idle)
	},
	'tasks.delete_idle_personal_group': {
		'task': 'tasks.delete_idle_personal_group',
		'schedule': timedelta(seconds=6*24*60*60), # execute every 6 days (hard deletion called on 1-on-1 groups that have gone idle)
	},
}

CELERY_TIMEZONE = 'UTC'

ABSOLUTE_URL_OVERRIDES = {
	'auth.user': lambda u: "/link/first_time/"
}
