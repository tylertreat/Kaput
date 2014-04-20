import os

from flask.ext.login import LoginManager

from google.appengine.api import app_identity


DEBUG = False

# Auto-set debug mode based on App Engine dev environ
if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
    DEBUG = True

login_manager = LoginManager()

HOST = 'https://%s' % app_identity.get_default_version_hostname()
KAPUT_WEBHOOK_ENDPOINT = '/v1/push'

GITHUB_CLIENT_ID = 'changeme'
GITHUB_CLIENT_SECRET = 'changeme'
GITHUB_REDIRECT_URI = '/github_authorized'


try:
    import settingslocal
except ImportError:
    settingslocal = None

if settingslocal:
    for setting in dir(settingslocal):
        globals()[setting.upper()] = getattr(settingslocal, setting)

if DEBUG:
    HOST = 'http://localhost:8080'

KAPUT_WEBHOOK_URI = '%s/api%s' % (HOST, KAPUT_WEBHOOK_ENDPOINT)

