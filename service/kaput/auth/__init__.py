from flask_oauth import OAuth

from kaput import settings


oauth = OAuth()


GITHUB_SCOPES = ['repo', 'user:email', 'admin:repo_hook']


github = oauth.remote_app(
    'github',
    base_url='https://www.github.com/login/',
    authorize_url='https://github.com/login/oauth/authorize',
    request_token_url=None,
    request_token_params={
        'scope': ','.join(GITHUB_SCOPES),
        'response_type': 'code',
    },
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_method='POST',
    consumer_key=settings.GITHUB_CLIENT_ID,
    consumer_secret=settings.GITHUB_CLIENT_SECRET
)

