import os


DEBUG = False

# Auto-set debug mode based on App Engine dev environ
if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'):
    DEBUG = True


# Flask-Cache settings
CACHE_TYPE = 'gaememcached'

GITHUB_OAUTH_CLIENT_ID = 'changeme'
GITHUB_OAUTH_CLIENT_SECRET = 'changeme'


try:
    import settingslocal
except ImportError:
    settingslocal = None

if settingslocal:
    for setting in dir(settingslocal):
        globals()[setting.upper()] = getattr(settingslocal, setting)

