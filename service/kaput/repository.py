import logging
import re

from google.appengine.ext import ndb

from furious import context
from furious.async import defaults

from kaput.services import gh
from kaput.user import User


COMMIT_QUEUE = 'commit-aggregation'


class Repository(ndb.Model):
    """Git repository."""

    # The name of the repo.
    name = ndb.StringProperty()

    # The User this repo belongs to.
    owner = ndb.KeyProperty(kind=User)

    # Process webhooks for this repo?
    enabled = ndb.BooleanProperty(default=False)


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


class CommitChunk(ndb.Model):
    """Granular source code diff hunk in a commit."""

    commit = ndb.KeyProperty(kind=Commit)
    filename = ndb.StringProperty()
    start_line = ndb.IntegerProperty()
    line_count = ndb.IntegerProperty(default=0)
    timestamp = ndb.DateTimeProperty()


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
                args=(repo.key.id(), commit['id'], owner.github_access_token))


@defaults(queue=COMMIT_QUEUE)
def process_commit(repo_id, commit_id, owner_token):
    """Process a single commit that was made to a repo by collecting data for
    it.

    Args:
        repo_id: the id for the repo the commit was for.
        commit_id: the SHA hash of the commit.
        owner_token: OAuth access token for the owner of the repo.
    """

    # TODO: error handling/retries
    repo = Repository.get_by_id(repo_id)
    github = gh.client(owner_token)
    user = github.get_user()

    gh_commit = user.get_repo(repo.name).get_commit(commit_id)
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

    chunks = []

    for commit_file in gh_commit.files:
        chunks.extend(_parse_chunks(commit, commit_file))

    logging.debug('Saving %d commit chunks' % len(chunks))
    ndb.put_multi(chunks)


def _parse_chunks(commit, commit_file):
    """Parse CommitChunks from the commit patch on the committed file.

    Args:
        commit: Commit instance the file pertains to.
        commit_file: File instance for the committed file.

    Returns:
        list of CommitChunks.
    """

    patch = commit_file.patch

    chunks = []

    for patch in re.findall('@@(.*)@@', patch, re.IGNORECASE):
        _, after = patch.strip().split(' ')

        start_line, line_count = after.split(',')

        chunks.append(CommitChunk(parent=commit.key, commit=commit.key,
                                  filename=commit_file.filename,
                                  start_line=int(start_line),
                                  line_count=int(line_count),
                                  timestamp=commit.author_date))

    return chunks

