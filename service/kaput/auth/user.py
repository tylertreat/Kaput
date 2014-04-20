import logging

from google.appengine.ext import ndb

from flask.ext.login import login_user
from flask.ext.login import UserMixin
from github import Github

from kaput.settings import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class User(ndb.Model, UserMixin):

    username = ndb.StringProperty()
    email = ndb.StringProperty()
    github_token = ndb.StringProperty()

    def __repr__(self):
        return '<User %r>' % self.username

    def get_id(self):
        return self.key.id()

    def is_authenticated(self):
        return self.github_token is not None

    def owns(self, repos):
        """Return True if the User is the owner of the given Repositories.

        Args:
            repos: Repository or list of Repositories.

        Returns:
            True if the User owns all Repositories, False otherwise.
        """

        if not isinstance(repos, list):
            repos = [repos]

        for repo in repos:
            if repo.owner.id() != self.key.id():
                return False

        return True

    @property
    def github_user(self):
        if not hasattr(self, '_github_user') or not self._github_user:
            self._github_user = Github(self.github_token).get_user()

        return self._github_user

    @property
    def github_orgs(self):
        if not hasattr(self, '_github_orgs') or not self._github_orgs:
            self._github_orgs = self.github_user.get_orgs()

        return self._github_orgs

    @property
    def github_repos(self):
        if not hasattr(self, '_github_repos') or not self._github_repos:
            self._github_repos = self.github_user.get_repos(type='owner')

        return self._github_repos

    def get_github_repo(self, name):
        return self.github_user.get_repo(name)


def login(credentials):
    """Log in the user associated with the given GitHub credentials. If a user
    entity does not exist for the user, create one.

    Args:
        credentials: dict containing GitHub oauth credentials.
    """

    access_token = credentials['access_token']
    gh_user = Github(access_token).get_user()

    user = User.get_by_id('github_%s' % gh_user.id)

    if user:
        user.github_token = access_token
    else:
        logging.debug('Creating new User entity for %s' % gh_user.login)
        user = User(id='github_%s' % gh_user.id, username=gh_user.login,
                    email=gh_user.email, github_token=access_token)

    user.put()
    login_user(user)

