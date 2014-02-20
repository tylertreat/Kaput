import os

from flask.ext.login import LoginManager

from google.appengine.api import app_identity


DEBUG = False

# Auto-set debug mode based on App Engine dev environ
if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
    DEBUG = True

login_manager = LoginManager()

# Flask-Cache settings
CACHE_TYPE = 'gaememcached'

GITHUB_CLIENT_ID = 'changeme'
GITHUB_CLIENT_SECRET = 'changeme'
GITHUB_CALLBACK_URL = \
    'https://%s/authorized' % app_identity.get_default_version_hostname()


try:
    import settingslocal
except ImportError:
    settingslocal = None

if settingslocal:
    for setting in dir(settingslocal):
        globals()[setting.upper()] = getattr(settingslocal, setting)

