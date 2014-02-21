import json
import logging

from flask import request

from kaput.api.blueprint import blueprint
from kaput.repository import Repository


@blueprint.route('/v1/exception', methods=['POST'])
def process_exception():
    # TODO: Implement
    data = request.data
    logging.debug('data: %s' % data)

    return data, 200


@blueprint.route('/v1/push', methods=['POST'])
def process_git_push():
    push_data = json.loads(request.data)

    repo_id = push_data['repository']['id']
    repo = Repository.get_by_id('github_%s' % repo_id)

    if not repo:
        return 'Repo github_%s not found' % repo_id, 404

    if not repo.enabled:
        return 'Repo github_%s disabled' % repo_id, 200

    # TODO: fan out to taskqueue.

    return 'Processing github_%s' % repo_id, 200

