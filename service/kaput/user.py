from functools import wraps
import logging

from google.appengine.ext import ndb

from flask.ext.login import UserMixin

from kaput.services import gh
from kaput.settings import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


def github_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        user = args[0]

        if not user.github_access_token:
            logging.warn('No GitHub token for user %s' % user.key.id())
            return None

        return func(*args, **kwargs)

    return wrapper


class User(ndb.Model, UserMixin):

    username = ndb.StringProperty()
    email = ndb.StringProperty()
    github_access_token = ndb.StringProperty()

    def get_id(self):
        return self.key.id()

    @github_required
    def github_client(self):
        return gh.client(self.github_access_token)

    @github_required
    def get_github_repos(self):
        return self.github_client().get_user().get_repos(type='owner')

    @github_required
    def get_github_repo(self, name):
        return self.github_client().get_user().get_repo(name)

