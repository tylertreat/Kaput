from httplib2 import Http
import logging
import json

from flask import redirect

from kaput import settings


AUTH_URL = 'https://github.com/login/oauth/authorize'
ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
OAUTH_SCOPES = 'repo,user:email'


def authorize():
    """Kick off the OAuth web server flow. This will redirect the user to
    GitHub for authorization, after which they will be redirected back.
    """

    return redirect('%s?scope=%s&client_id=%s' % (AUTH_URL, OAUTH_SCOPES,
                                                  settings.GITHUB_CLIENT_ID))


def exchange_for_token(session_code):
    """Exchange the temporary session code for an OAuth access token."""

    payload = json.dumps({
        'client_id': settings.GITHUB_CLIENT_ID,
        'client_secret': settings.GITHUB_CLIENT_SECRET,
        'code': session_code
    })

    headers = {
        'Accept': 'application/json', 'Content-Type':
        'application/json'
    }

    resp, content = Http().request(ACCESS_TOKEN_URL, method='POST',
                                   body=payload, headers=headers)

    if resp.status != 200:
        logging.error('Failed to exchange GitHub access token')
        return None

    content = json.loads(content)

    if 'access_token' not in content:
        logging.error('Failed to exchange GitHub access token')
        return None

    return content.get('access_token')

