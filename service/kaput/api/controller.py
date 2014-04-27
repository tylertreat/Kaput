import ipaddress
import json
import logging

from google.appengine.api import urlfetch

from flask import request

from kaput import settings
from kaput.api.blueprint import blueprint
from kaput.report import process_exception
from kaput.repository import process_repo_push
from kaput.repository import process_release
from kaput.repository import Repository


GITHUB_META_ENDPOINT = 'https://api.github.com/meta'


@blueprint.route('/v1/exception', methods=['POST'])
def handle_exception():
    # TODO: Client secret authentication.
    data = request.data
    logging.debug('Exception: %s' % data)

    process_exception(json.loads(data))

    return 'Processing exception', 200


@blueprint.route(settings.PUSH_WEBHOOK_ENDPOINT, methods=['POST'])
def process_github_push():
    if not _verify_webhook_origin(request.remote_addr):
        return '', 403

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


@blueprint.route(settings.RELEASE_WEBHOOK_ENDPOINT, methods=['POST'])
def process_github_release():
    if not _verify_webhook_origin(request.remote_addr):
        return '', 403

    release_data = json.loads(request.data)

    process_release(release_data['repository']['id'], release_data['release'])

    return '', 200


def _verify_webhook_origin(origin_ip):
    """Verify that the given IP address is a valid GitHub webhook origin.

    Args:
        origin_ip: IP address to verify

    Returns:
        True if the origin is valid, False if not.
    """

    result = urlfetch.fetch(GITHUB_META_ENDPOINT)

    if result.status_code != 200:
        raise Exception('Failed to retrieve GitHub origins')

    hook_origins = json.loads(result.content)['hooks']

    for valid_origin in hook_origins:
        ip = ipaddress.ip_address(u'%s' % origin_ip)
        if ipaddress.ip_address(ip) in ipaddress.ip_network(valid_origin):
            return True

    return False

