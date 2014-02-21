from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask.ext.login import login_user
from flask.ext.login import logout_user

from kaput.services import gh
from kaput.repository import Repository
from kaput.user import User
from kaput.view.blueprint import blueprint


@blueprint.route('/')
def index():
    return render_template('index.html', user=current_user)


@login_required
@blueprint.route('/repo/<name>')
def repo(name):
    gh_repo = current_user.get_github_repo(name)

    if not gh_repo:
        return 'No repo %s' % name, 404

    repo = Repository.get_by_id('github_%s' % gh_repo.id)

    if not repo:
        repo = Repository(id='github_%s' % gh_repo.id, name=name,
                          owner=current_user.key)
        repo.put()

    return render_template('repo.html', repo=repo)


@login_required
@blueprint.route('/repo/<name>/enable')
def enable_repo(name):
    enable = request.args['on'] == 'true'
    gh_repo = current_user.get_github_repo(name)

    if not gh_repo:
        return 'No repo %s' % name, 404

    repo = Repository.get_by_id('github_%s' % gh_repo.id)

    if not repo:
        repo = Repository(id='github_%s' % gh_repo.id, name=name,
                          owner=current_user.key)

    repo.enabled = enable
    repo.put()

    return redirect('/repo/%s' % name)


@blueprint.route('/login')
def login():
    if current_user.is_authenticated():
        return redirect('/')

    return gh.authorize()


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@blueprint.route('/authorized')
def authorized():
    session_code = request.args.get('code')
    access_token = gh.exchange_for_token(session_code)

    next_url = request.args.get('next') or '/'

    if not access_token:
        flash("Authorization failed :(")
        return redirect(next_url)

    user = User.query().filter(User.github_access_token == access_token).get()

    if not user:
        gh_user = gh.client().get_user()
        user = User(id='github_%s' % gh_user.id, username=gh_user.login,
                    email=gh_user.email, github_access_token=access_token)
        user.put()

    login_user(user)

    return redirect('/')

