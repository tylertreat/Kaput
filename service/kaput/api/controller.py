import json
import logging

from flask import request

from kaput.api.blueprint import blueprint
from kaput.report import process_exception
from kaput.repository import process_repo_push
from kaput.repository import Repository


@blueprint.route('/v1/exception', methods=['POST'])
def handle_exception():
    # TODO: Client secret authentication.
    data = request.data
    logging.debug('Exception: %s' % data)

    process_exception(json.loads(data))

    return 'Processing exception', 200


@blueprint.route('/v1/push', methods=['POST'])
def process_git_push():
    # TODO: Verify request origin.
    push_data = json.loads(request.data)

    repo_id = push_data['repository']['id']
    repo = Repository.get_by_id('github_%s' % repo_id)

    if not repo:
        logging.error('Repo github_%s not found' % repo_id)
        return 'Repo github_%s not found' % repo_id, 404

    if not repo.enabled:
        logging.debug('Repo github_%s disabled' % repo_id)
        return 'Repo github_%s disabled' % repo_id, 200

    owner = repo.owner.get()

    if not owner:
        logging.error('Owner not found for repo github_%s' % repo_id)
        return 'Owner not found for repo github_%s' % repo_id

    process_repo_push(repo, owner, push_data)

    return 'Processing github_%s' % repo_id, 200

