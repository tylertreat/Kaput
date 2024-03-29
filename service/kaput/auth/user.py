from datetime import datetime
import logging

from google.appengine.api import memcache
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import ndb

from flask.ext.login import login_user
from flask.ext.login import UserMixin
from furious import context
from furious.async import defaults
from github import Github

from kaput.services import gh
from kaput.settings import login_manager
from kaput.utils import SerializableMixin


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class User(ndb.Model, UserMixin, SerializableMixin):

    username = ndb.StringProperty()
    primary_email = ndb.StringProperty()
    emails = ndb.StringProperty(repeated=True)
    github_token = ndb.StringProperty()
    last_synced = ndb.DateTimeProperty(required=False, indexed=False)
    active_repo = ndb.KeyProperty(kind='Repository', required=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def to_dict(self):
        return super(User, self).to_dict_(
            excludes=('github_token', 'key'),
            includes=('is_authenticated', 'repos'))

    def update(self, data):
        self.username = data.get('username', self.username)
        self.primary_email = data.get('primary_email', self.primary_email)
        self.emails = data.get('emails', self.emails)
        repo_id = data.get('active_repo')
        if repo_id:
            self.active_repo = ndb.Key('Repository', repo_id)

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
        return gh.get_user(self)

    @property
    def github_repos(self):
        return gh.get_repos(self)

    @property
    def repos(self):
        from kaput.repository import Repository
        return Repository.query(Repository.owner == self.key).fetch()

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
        emails, primary_email = _get_email_addresses(gh_user)
        user = User(id='github_%s' % gh_user.id, username=gh_user.login,
                    primary_email=primary_email, emails=emails,
                    github_token=access_token)

    user.put()
    login_user(user)


def _get_email_addresses(gh_user):
    """Retrieve a list of the user's verified email addresses and their primary
    email address.

    Args:
        gh_user: GitHub AuthenticatedUser instance.

    Returns:
        tuple containing a list of the user's verified email addresses and
        their primary email address.
    """

    emails = []
    primary = None

    for email_dict in gh_user.get_emails():
        if not email_dict['verified']:
            continue

        if email_dict['primary']:
            primary = email_dict['email']

        emails.append(email_dict['email'])

    return emails, primary


@defaults(queue='user-sync')
def sync_users(cursor=None):
    """Insert tasks to sync Users with GitHub.

    Args:
        cursor: urlsafe cursor to begin fetching users at.
    """

    query = User.query()
    if cursor:
        cursor = Cursor(urlsafe=cursor)

    keys, cursor, more = query.fetch_page(100, start_cursor=cursor,
                                          keys_only=True)

    with context.new() as ctx:
        logging.debug('Inserting task to sync %s user accounts' % len(keys))
        ctx.add(target=_sync_users, args=([key.id() for key in keys],))

        if more:
            ctx.add(target=sync_users, kwargs={'cursor': cursor.urlsafe()})


@defaults(queue='user-sync')
def _sync_users(user_ids):
    """Sync Users with GitHub.

    Args:
        user_ids: list of ids for users to sync.
    """

    keys = [ndb.Key(User, user_id) for user_id in user_ids]
    users = filter(None, ndb.get_multi(keys))

    for user in users:
        sync_github_user(user)


def sync_github_user(user):
    """Sync the given User with its GitHub account.

    Args:
        user: the User to sync.
    """
    from kaput import repository

    logging.debug('Syncing %s' % user)

    # Sync repos.
    repository.sync_repos(user)

    # Sync GitHub info.
    gh_user = user.github_user
    user.email = gh_user.email
    user.username = gh_user.login

    user.last_synced = datetime.utcnow()
    user.put()

