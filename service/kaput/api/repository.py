import json

from flask.ext.login import current_user
from flask.ext.login import login_required
from furious.async import Async

from kaput.api.blueprint import blueprint
from kaput.repository import Repository


@login_required
@blueprint.route('/v1/repo')
def get_repos():
    """Get the user's Repositories."""

    repos = Repository.query().filter(
        Repository.owner == current_user.key).fetch()

    repos = [repo.to_dict() for repo in repos]
    return json.dumps(repos), 200


@login_required
@blueprint.route('/v1/github/repo')
def get_github_repos():
    """Get the names of the user's GitHub repositories."""

    repos = current_user.get_github_repos()
    return json.dumps([{'id': repo.id, 'name': repo.name}
                       for repo in repos]), 200


@login_required
@blueprint.route('/v1/repo/sync', methods=['POST'])
def sync_repos():
    """Sync the user's GitHub repos by creating a Repository entity for each
    one.
    """
    from kaput.repository import sync_repos

    Async(target=sync_repos, args=(current_user.key.id(),)).start()

    return '', 200

