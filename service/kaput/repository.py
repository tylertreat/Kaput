from datetime import datetime
import logging
import re

from google.appengine.api import memcache
from google.appengine.ext import ndb

from furious import context
from furious.async import defaults
from github import Github

from kaput import settings
from kaput.auth.user import User
from kaput.services import gh
from kaput.utils import chunk
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

    def get_webhooks(self):
        """Get the Kaput GitHub webhooks for this repository.

        Returns:
            list of Hook instances.
        """

        return gh.get_webhooks(self, (settings.PUSH_WEBHOOK_URI,
                                      settings.RELEASE_WEBHOOK_URI))

    def create_webhooks(self):
        """Create GitHub webhooks for this repository. This is intended to be
        idempotent, meaning it will check to see if the hooks already exist
        before creating them.

        Returns:
            True if the webhooks were successfully created or already exist,
            False if they failed to be created.
        """

        return gh.create_webhook(self, settings.PUSH_WEBHOOK_URI) and \
            gh.create_webhook(self, settings.RELEASE_WEBHOOK_URI,
                              events=['release'])

    def delete_webhooks(self):
        """Delete the GitHub webhooks for this repository."""

        gh.delete_webhook(self, settings.PUSH_WEBHOOK_URI)
        gh.delete_webhook(self, settings.RELEASE_WEBHOOK_URI)


class Commit(ndb.Model):
    """Commit to a Git repository."""

    author = ndb.KeyProperty(kind=User, required=False)
    author_name = ndb.StringProperty(indexed=False)
    author_email = ndb.StringProperty(indexed=False)
    author_date = ndb.DateTimeProperty(indexed=False)
    committer = ndb.KeyProperty(kind=User, required=False)
    committer_name = ndb.StringProperty(indexed=False)
    committer_email = ndb.StringProperty(indexed=False)
    committer_date = ndb.DateTimeProperty(indexed=False)
    message = ndb.TextProperty(indexed=False, required=False)
    release = ndb.KeyProperty(required=False)


class CommitHunk(ndb.Model):
    """Granular source code diff hunk in a commit."""

    commit = ndb.KeyProperty(kind=Commit)
    filename = ndb.StringProperty()
    lines = ndb.IntegerProperty(repeated=True)
    timestamp = ndb.DateTimeProperty()


class Release(ndb.Model):
    """Git repository release."""

    tag_name = ndb.StringProperty(indexed=False)
    name = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)
    prerelease = ndb.BooleanProperty(indexed=False)
    created = ndb.DateTimeProperty(indexed=False)
    published = ndb.DateTimeProperty(indexed=False)
    url = ndb.StringProperty(indexed=False)


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

    to_create = [Repository(id='github_%s' % repo.id, name=repo.name,
                            description=repo.description, owner=user.key)
                 for repo in to_create]

    logging.debug('Creating %d Repositories' % len(to_create))
    ndb.put_multi(to_create)

    repos = filter(None, repos) + to_create
    memcache.set('kaput:repos:%s' % user.key.id(), repos)

    return repos


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
        repo.create_webhooks()
    else:
        repo.delete_webhooks()


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


def process_release(repo_id, release_data):
    """Process a newly created repo release. Create a Release entity for it and
    tag any untagged Commits with the Release.

    Args:
        repo_id: the id of the repo the release belongs to.
        release_data: dict containing release data.

    Returns:
        the created Release entity.
    """

    repo = Repository.get_by_id('github_%s' % repo_id)

    if not repo:
        raise Exception('Repo with id github_%s does not exist' % repo_id)

    created = datetime.strptime(release_data['created_at'],
                                '%Y-%m-%dT%H:%M:%SZ')
    published = datetime.strptime(release_data['published_at'],
                                  '%Y-%m-%dT%H:%M:%SZ')

    release = Release(id='github_%s' % release_data['id'],
                      parent=repo.key,
                      tag_name=release_data['tag_name'],
                      name=release_data['name'],
                      description=release_data.get('body'),
                      prerelease=release_data['prerelease'],
                      created=created,
                      published=published,
                      url=release_data['html_url'])

    release.put()
    _tag_commits(repo, release)

    return release


def _tag_commits(repo, release):
    """Tag any untagged Commits with the given Release.

    Args:
        repo: the Repository to tag Commits for.
        release: the Release to tag with.
    """

    query = Commit.query(ancestor=repo.key).filter(Commit.release == None)

    with context.new() as ctx:
        # Associate past commits with the release. Fan out tasks to process
        # in batches.
        cursor = None
        while True:
            commit_keys, cursor, more = query.fetch_page(
                500, start_cursor=cursor, keys_only=True)

            for keys in chunk(commit_keys, 10):
                logging.debug('Inserting task to tag commit release')
                ctx.add(target=tag_commit,
                        args=(repo.key.id(), release.key.id(),
                              [key.id() for key in keys]))

            if not more or not commit_keys:
                break


def tag_commit(repo_id, release_id, commit_ids):
    """Tag the given Commits with a Release.

    Args:
        repo_id: the id of the Repository.
        release_id: the id of the Release to tag with.
        commit_ids: the ids of the Commits to tag.
    """

    repo = Repository.get_by_id(repo_id)
    release = Release.get_by_id(release_id, parent=repo.key)
    commits = filter(None, ndb.get_multi(
        [ndb.Key(Repository, repo_id, Commit, commit_id)
         for commit_id in commit_ids])
    )

    for commit in commits:
        commit.release = release.key

    logging.debug('Tagging %s commits with release %s' % (len(commits),
                                                          release))
    ndb.put_multi(commits)


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
    repo = Repository.get_by_id(repo_id)
    gh_commit = _get_commit(repo.name, commit_id, owner.github_token)
    author = gh_commit.commit.author
    committer = gh_commit.commit.committer

    author_user = User.get_by_id('github_%s' % gh_commit.author.id)
    committer_user = User.get_by_id('github_%s' % gh_commit.committer.id)
    author_key = author_user.key if author_user else None
    committer_key = committer_user.key if committer_user else None

    commit = Commit(
        id=commit_id, parent=repo.key, author=author_key,
        author_name=author.name, author_email=author.email,
        author_date=author.date, committer=committer_key,
        committer_name=committer.name, committer_email=committer.email,
        committer_date=committer.date, message=gh_commit.commit.message)

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

        hunks.append(CommitHunk(parent=commit.key,
                                commit=commit.key,
                                filename=commit_file.filename,
                                lines=lines,
                                timestamp=commit.author_date))

    return hunks

