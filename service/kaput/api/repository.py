import json
import logging

from flask import request
from flask.ext.login import current_user
from flask.ext.login import login_required

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
@blueprint.route('/v1/repo/sync', methods=['POST'])
def sync_repos():
    """Sync the user's GitHub repos by creating a Repository entity for each
    one if an entity doesn't already exist.
    """
    from kaput.repository import sync_repos

    repos = sync_repos(current_user)

    return json.dumps([repo.to_dict() for repo in repos]), 200


@login_required
@blueprint.route('/v1/repo', methods=['PUT'])
def update_repo():
    """Update an existing Repository entity."""

    update = json.loads(request.data)
    repo_id = update.get('id')
    if not repo_id:
        return json.dumps({'message': 'Missing required id field'}), 400

    repo = Repository.get_by_id(repo_id)

    if not repo:
        return json.dumps({'message': 'Repo %s does not exist' % repo_id}), 404

    if not current_user.owns(repo):
        return json.dumps({'message': 'User %s does not own Repo %s' %
                           (current_user.key.id(), repo_id)}), 403

    enabled = update.get('enabled', repo.enabled)
    repo.enabled = enabled
    repo.put()
    logging.debug('Updated Repository %s' % repo.key.id())

    return json.dumps(repo.to_dict()), 200

