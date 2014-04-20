import logging

from flask import redirect
from flask import render_template
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.login import logout_user

from kaput import settings
from kaput.auth import github
from kaput.auth import user
from kaput.view.blueprint import blueprint


@blueprint.route('/')
def index():
    return render_template('index.html', user=current_user)


@blueprint.route('/login')
def login():
    if current_user.is_authenticated():
        return redirect('/#/dashboard')

    callback = '%s%s' % (settings.HOST, settings.GITHUB_REDIRECT_URI)

    logging.debug('Redirecting to GitHub for authorization: %s' % callback)
    return github.authorize(callback=callback)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@blueprint.route(settings.GITHUB_REDIRECT_URI)
@github.authorized_handler
def github_authorized(credentials):
    """GitHub OAuth callback that is redirect to after the user consents."""
    user.login(credentials)
    return redirect('/#/dashboard')

