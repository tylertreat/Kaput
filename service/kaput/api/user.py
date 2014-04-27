import json

from flask import request

from flask.ext.login import current_user
from flask.ext.login import login_required

from kaput.api.blueprint import blueprint
from kaput.utils import EntityEncoder


@login_required
@blueprint.route('/v1/user')
def get_user():
    """Get the current session User."""

    return json.dumps(current_user.to_dict(), cls=EntityEncoder), 200


@login_required
@blueprint.route('/v1/user/sync', methods=['POST'])
def sync_github():
    """Sync the current session User with GitHub."""
    from kaput.auth.user import sync_github_user

    sync_github_user(current_user)

    return json.dumps(current_user.to_dict(), cls=EntityEncoder), 200


@login_required
@blueprint.route('/v1/user', methods=['PUT'])
def update_user():
    """Update the current session User."""

    user_data = json.loads(request.data)

    current_user.update(user_data)
    current_user.put()

    return json.dumps(current_user.to_dict(), cls=EntityEncoder), 200

