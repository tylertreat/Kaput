from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from kaput import github
from kaput.user import User
from kaput.view.blueprint import blueprint


@blueprint.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.get_by_id(session['user_id'])


@blueprint.route('/')
def index():
    user = g.user

    return render_template('index.html', user=user)


@github.access_token_getter
def token_getter():
    user = g.user
    if user:
        return user.github_access_token


@blueprint.route('/login')
def login():
    if session.get('user_id', None) is None:
        return github.authorize(scope='repo,user:email')
    else:
        return 'Already logged in'


@blueprint.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


@blueprint.route('/user')
def user():
    return str(github.get('user'))


@blueprint.route('/authorized')
@github.authorized_handler
def authorized(access_token):
    next_url = request.args.get('next') or '/'

    if not access_token:
        flash("Authorization failed :(")
        return redirect(next_url)

    user = User.query().filter(User.github_access_token == access_token).get()

    if not user:
        user = User(github_access_token=access_token)

    user.put()

    session['user_id'] = user.key.id()

    return redirect('/')

