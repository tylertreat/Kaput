import logging
import re

from google.appengine.ext import ndb

from furious import context
from furious.async import defaults
from github import Github

from kaput import settings
from kaput.auth.user import User
from kaput.utils import SerializableMixin


COMMIT_QUEUE = 'commit-aggregation'


class Repository(ndb.Model, SerializableMixin):
    """Git repository."""

    name = ndb.StringProperty()
    description = ndb.StringProperty(indexed=False)
    owner = ndb.KeyProperty(kind=User)
    enabled = ndb.BooleanProperty(default=False)

    def __repr__(self):
        return '<Repository %r>' % self.name

    def to_dict(self):
        return super(Repository, self).to_dict_(excludes=('key',))

    def get_webhook(self):
        """Get the Kaput GitHub webhook for this repository.

        Returns:
            Hook instance or None if the hook doesn't exist.
        """

        repo = self.owner.get().get_github_repo(self.name)
        for hook in repo.get_hooks():
            if hook.config.get('url') == settings.KAPUT_WEBHOOK_URI:
                return hook

        return None

    def create_webhook(self):
        """Create a GitHub webhook for this repository. This is intended to be
        idempotent, meaning it will check to see if the hook already exists
        before creating it.

        Returns:
            True if the webhook was successfully created or already exists,
            False if it failed to be created.
        """

        if self.get_webhook():
            logging.debug('%s already has Kaput webhook' % self)
            return True

        repo = self.owner.get().get_github_repo(self.name)
        hook = repo.create_hook(
            'web', {'url': settings.KAPUT_WEBHOOK_URI, 'content_type': 'json'},
            events=['push'], active=True)

        return hook is not None

    def delete_webhook(self):
        """Delete the GitHub webhook for this repository."""

        hook = self.get_webhook()

        if hook:
            logging.debug('Deleting Kaput webhook for %s' % self)
            hook.delete()


class Commit(ndb.Model):
    """Commit to a Git repository."""

    repo = ndb.KeyProperty(kind=Repository)
    sha = ndb.StringProperty(indexed=False)
    author = ndb.KeyProperty(kind=User, required=False)
    author_name = ndb.StringProperty(indexed=False)
    author_email = ndb.StringProperty(indexed=False)
    author_date = ndb.DateTimeProperty(indexed=False)
    committer = ndb.KeyProperty(kind=User, required=False)
    committer_name = ndb.StringProperty(indexed=False)
    committer_email = ndb.StringProperty(indexed=False)
    committer_date = ndb.DateTimeProperty(indexed=False)
    message = ndb.TextProperty(indexed=False, required=False)


class CommitHunk(ndb.Model):
    """Granular source code diff hunk in a commit."""

    commit = ndb.KeyProperty(kind=Commit)
    filename = ndb.StringProperty()
    lines = ndb.IntegerProperty(repeated=True)
    timestamp = ndb.DateTimeProperty()


def sync_repos(user):
    """Sync the user's GitHub repos by creating a Repository entity for each
    one.

    Args:
        user: the User to sync repos for.

    Returns:
        list of user's repositories.
    """

    logging.debug('Syncing Repositories for %s' % user)
    github_repos = user.github_repos
    repo_keys = [ndb.Key(Repository, 'github_%s' % repo.id) for repo in
                 github_repos]
    repos = ndb.get_multi(repo_keys)

    to_create = [github_repos[index]
                 for index, repo in enumerate(repos) if not repo]

    to_create = [Repository(id='github_%s' % repo.id, parent=user.key,
                            name=repo.name, description=repo.description,
                            owner=user.key)
                 for repo in to_create]

    logging.debug('Creating %d Repositories' % len(to_create))
    ndb.put_multi(to_create)

    return filter(None, repos) + to_create


@ndb.transactional
def enable_repo(repo, enabled):
    """Update the given repo by enabling/disabling it. This will not only
    update the Repo model, but also create or delete the GitHub webhook on the
    repo if it was enabled or disabled respectively.

    Args:
        repo: the Repo to update.
        enabled: bool indicating if the Repo is enabled or disabled.
    """

    repo.enabled = enabled
    logging.debug('Saving %s, enabled: %s' % (repo, enabled))
    repo.put()

    if enabled:
        repo.create_webhook()
    else:
        repo.delete_webhook()


def process_repo_push(repo, owner, push_data):
    """Process a push to a repo by collecting data for each commit

    Args:
        repo: Repository instance of the repo that was pushed to.
        owner: User instance of the owner of the repo pushed to.
        push_data: dict containing data for the push.
    """

    logging.debug('Processing push to repo %s' % repo.key.id())

    with context.new() as ctx:
        # Fan out tasks for each commit in the push.
        for commit in push_data['commits']:
            logging.debug('Inserting task for commit %s' % commit['id'])

            ctx.add(
                target=process_commit,
                args=(repo.key.id(), commit['id'], owner.key.id()))

    logging.debug('Inserted %d fan-out tasks' % ctx.insert_success)


@defaults(queue=COMMIT_QUEUE)
def process_commit(repo_id, commit_id, owner_id):
    """Process a single commit that was made to a repo by collecting data for
    it.

    Args:
        repo_id: the id for the repo the commit was for.
        commit_id: the SHA hash of the commit.
        owner_id: id of the owner of the repo.
    """

    owner = User.get_by_id(owner_id)
    repo = Repository.get_by_id(repo_id, parent=owner.key)
    gh_commit = _get_commit(repo.name, commit_id, owner.github_token)
    author = gh_commit.commit.author
    committer = gh_commit.commit.committer

    author_user = User.get_by_id('github_%s' % gh_commit.author.id)
    committer_user = User.get_by_id('github_%s' % gh_commit.committer.id)

    commit = Commit(
        id=commit_id, parent=repo.key, repo=repo.key, sha=commit_id,
        author=author_user.key, author_name=author.name,
        author_email=author.email, author_date=author.date,
        committer=committer_user.key, committer_name=committer.name,
        committer_email=committer.email, committer_date=committer.date,
        message=gh_commit.commit.message)

    logging.debug('Saving commit %s' % commit_id)
    commit.put()

    hunks = []

    for commit_file in gh_commit.files:
        hunks.extend(_parse_hunks(commit, commit_file))

    logging.debug('Saving %d commit hunks' % len(hunks))
    ndb.put_multi(hunks)


def _get_commit(repo_name, commit_id, owner_token):
    github = Github(owner_token)
    user = github.get_user()
    return user.get_repo(repo_name).get_commit(commit_id)


def _parse_hunks(commit, commit_file):
    """Parse CommitHunks from the commit patch on the committed file.

    Args:
        commit: Commit instance the file pertains to.
        commit_file: File instance for the committed file.

    Returns:
        list of CommitHunks.
    """

    patch = commit_file.patch

    hunks = []

    for patch in re.findall('@@(.*)@@', patch, re.IGNORECASE):
        _, after = patch.strip().split(' ')

        if ',' in after:
            start_line, line_count = after.split(',')
        else:
            start_line, line_count = after, 1

        lines = range(int(start_line), int(start_line) + int(line_count))

        hunks.append(CommitHunk(parent=commit.key, commit=commit.key,
                                filename=commit_file.filename,
                                lines=lines,
                                timestamp=commit.author_date))

    return hunks

