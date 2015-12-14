# Django settings for unconnectedreddit project.
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_DIR = os.path.dirname(os.path.dirname(__file__))

#print "CHECKING_HEROKU_OR_AZURE!"
ON_HEROKU = os.environ.get('ON_HEROKU')
ON_AZURE = os.environ.get('ON_AZURE')

#ON_AZURE = '1'
#awssecretkey='PAxpBD2Xc2Hbd0IiL+KjMYAaZwDXClY9BVSUKvY6'
#awsaccesskeyid='AKIAJEYMTQS5SDDAKKHA'
#heroku config:set ON_HEROKU=1 
#heroku ps:scale web=1 to put in a dyno

#DEBUG_TOOLBAR_PATCH_SETTINGS = False

#DEBUG_TOOLBAR_CONFIG = {
#    'SHOW_TOOLBAR_CALLBACK': 'unconnectedreddit.settings.show_toolbar',
#}

#git init
#git remote add origin https://github.com/mhb11/unconnectedredditpk.git
#git pull origin master
#git add <files>
#git push origin master	

if ON_HEROKU == '1':
	DEBUG=False
else:
	DEBUG=True

TEMPLATE_DEBUG = DEBUG

ADMINS = (
	('Hassan Baig', 'baig.hassan@gmail.com'),
	('Sophie Pervez', 'spz3113@gmail.com'),
	('Fahad Rao', 'fahadrao@gmail.com'),
)

MANAGERS = ADMINS

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']																																														

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Oral'

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
USE_TZ = True

GOOGLE_ANALYTICS_PROPERTY_ID = 'UA-68289796-1'

GOOGLE_ANALYTICS_SITE_SPEED = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = 'staticfiles'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

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
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
 #   'debug_toolbar.middleware.DebugToolbarMiddleware',
	'unconnectedreddit.middleware.XForwardedFor.XForwardedForMiddleware',
	'user_sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	#'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'unconnectedreddit.middleware.HellBanned.HellBannedMiddleware',
	#'request.middleware.RequestMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	#'mobi.middleware.MobileDetectionMiddleware',
	# Uncomment the next line for simple clickjacking protection:
	# 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

SESSION_ENGINE = 'user_sessions.backends.db'

#MOBI_DETECT_TABLET = True
#MOBI_USER_AGENT_IGNORE_LIST = ['ipad', 'android', 'iphone',]

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
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
	#'django.contrib.sessions',
	'user_sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'django.contrib.admin',
	'django.contrib.comments',
	'links',
	'unconnectedreddit',
	'south',
	'registration', #found at has@has-VirtualBox:~/.virtualenvs/unconnectedreddit/local/lib/python2.7/site-packages/registration/backends/simple$
	'bootstrap_pagination',
	'djcelery',
	'tweepy',
	'django.contrib.humanize',
	'analytical',
	'mathfilters',
	#'request',
    #'debug_toolbar',
	#'analytical',
	#'django_whoshere',
	# Uncomment the next line to enable admin documentation:
	# 'django.contrib.admindocs',
)

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
if ON_HEROKU == '1':
# Parse database configuration from $DATABASE_URL
	print "ON_HEROKU!"
	DATABASES = {
	'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
	}
	DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
	AWS_S3_FORCE_HTTP_URL = True
	AWS_QUERYSTRING_AUTH = False
	AWS_SECRET_ACCESS_KEY = os.environ.get('awssecretkey')
	AWS_ACCESS_KEY_ID = os.environ.get('awsaccesskeyid')
	AWS_S3_CALLING_FORMAT='boto.s3.connection.OrdinaryCallingFormat'
	AWS_STORAGE_BUCKET_NAME = 'damadam.pk'
elif ON_AZURE == '1':
	print "ON_AZURE!"
	DATABASE_URL = 'postgres://damadamrg.cloudapp.net:5432/damadam'
	DATABASES = {
	'default': dj_database_url.config(default=DATABASE_URL)
	}
	DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
	AZURE_ACCOUNT_NAME = 'damadamdatabasestorage'
	AZURE_ACCOUNT_KEY = 'pl8iUTruE2T1xN3z83wuLH5lpgUp0TcMS6g6pxEbfsS/ZH7wEKF0VED+78+KxOwq+TmKgmjazApyXpWWIsuEFw=='
	AZURE_CONTAINER = 'damadampkcontainer'
else:
# Parse database configuration from $DATABASE_URL
	print "NOT_ON_HEROKU_NOR_AZURE!"
	DEFAULT_FILE_STORAGE = 'storages.backends.azure_storage.AzureStorage'
	AZURE_ACCOUNT_NAME = 'damadamdatabasestorage'
	AZURE_ACCOUNT_KEY = 'pl8iUTruE2T1xN3z83wuLH5lpgUp0TcMS6g6pxEbfsS/ZH7wEKF0VED+78+KxOwq+TmKgmjazApyXpWWIsuEFw=='
	AZURE_CONTAINER = 'damadampkcontainer'
######################################################
#	DATABASES = {
#	'default': {
#		'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#		'NAME': 'database.db',                      # Or path to database file if using sqlite3.
		# The following settings are not used with sqlite3:
#		'USER': '',
#		'PASSWORD': '',
#		'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
#		'PORT': '',                      # Set to empty string for default.
#	}
#}
#######################################################
	DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
		'NAME': 'damadampakistan',                      # Or path to database file if using sqlite3.
		# The following settings are not used with sqlite3:
		'USER': 'hassan',
		'PASSWORD': 'asdasdASFDA234',
		'HOST': 'localhost',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
		'PORT': '',                      # Set to empty string for default.
	}
}


# Honor the 'X-Forwarded-Proto' header for request.is_secure()
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

import djcelery
djcelery.setup_loader()
# config settings for Celery Daemon

# Redis broker
BROKER_URL = 'redis://localhost:6379/0'

# List of modules to import when celery starts, in myapp.tasks form. 
CELERY_IMPORTS = ('links.tasks', )  

CELERY_ALWAYS_EAGER = False

# default RabbitMQ backend
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
#The backend is the resource which returns the results of a completed task from Celery. 6379 is the default port to the redis server.

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IGNORE_RESULT=True

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
	'tasks.rank_all': {
		'task': 'tasks.rank_all',
		'schedule': timedelta(seconds=30),
	},
}

CELERY_TIMEZONE = 'UTC'

REQUEST_TRAFFIC_MODULES = (
'request.traffic.UniqueVisitor',
#'request.traffic.UniqueVisit',
'request.traffic.Hit',
#'request.traffic.Error',
'request.traffic.UniqueUser',
)

REQUEST_LOG_USER = True

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda u: "/link/create/"
}