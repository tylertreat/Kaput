from functools import wraps

from google.appengine.api import users

from flask import abort
from flask import redirect
from flask import request


def admin_required(func):
    """Require App Engine admin credentials."""

    @wraps(func)
    def decorated_view(*args, **kwargs):
        user = users.get_current_user()
        if user:
            if not users.is_current_user_admin():
                abort(401)  # Unauthorized
            return func(*args, **kwargs)

        return redirect(users.create_login_url(request.url))

    return decorated_view

