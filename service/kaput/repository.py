import re

from google.appengine.ext import ndb

from furious import context
from furious.async import defaults

from kaput.services import gh
from kaput.user import User


COMMIT_QUEUE = 'commit-aggregation'


class Repository(ndb.Model):

    name = ndb.StringProperty()
    owner = ndb.KeyProperty(kind=User)
    enabled = ndb.BooleanProperty(default=False)


class Commit(ndb.Model):

    repo = ndb.KeyProperty(kind=Repository)
    sha = ndb.StringProperty(indexed=False)
    author_name = ndb.StringProperty(indexed=False)
    author_email = ndb.StringProperty(indexed=False)
    author_date = ndb.DateTimeProperty(indexed=False)
    committer_name = ndb.StringProperty(indexed=False)
    committer_email = ndb.StringProperty(indexed=False)
    committer_date = ndb.DateTimeProperty(indexed=False)
    message = ndb.TextProperty(indexed=False, required=False)


class CommitChunk(ndb.Model):

    commit = ndb.KeyProperty(kind=Commit)
    filename = ndb.StringProperty()
    start_line = ndb.IntegerProperty()
    line_count = ndb.IntegerProperty(default=0)


def process_repo_push(repo, owner, push_data):

    with context.new() as ctx:
        for commit in push_data['commits']:
            ctx.add(
                target=process_commit,
                args=(repo.key.id(), commit['id'], owner.github_access_token))


@defaults(queue=COMMIT_QUEUE)
def process_commit(repo_id, commit_id, owner_token):
    # TODO: error handling/retries
    repo = Repository.get_by_id(repo_id)
    github = gh.client(owner_token)

    gh_commit = github.get_repo(repo.name).get_commit(commit_id)
    author = gh_commit.commit.author
    committer = gh_commit.commit.committer

    commit = Commit(
        repo=repo.key, sha=commit_id, author_name=author.name,
        author_email=author.email, author_date=author.date,
        committer_name=committer.name, committer_email=committer.email,
        committer_date=committer.date, message=gh_commit.commit.message)

    chunks = []

    for commit_file in commit.files:
        chunks.extend(_parse_chunks(commit_file))

    ndb.put_multi([commit] + chunks)


def _parse_chunks(commit, commit_file):
    patch = commit_file.patch

    chunks = []

    for patch in re.findall('@@(.*)@@', patch, re.IGNORECASE):
        _, after = patch.strip().split(' ')

        start_line, line_count = after.split(',')

        chunks.append(CommitChunk(commit=commit.key,
                                  filename=commit_file.filename,
                                  start_line=start_line,
                                  line_count=line_count))

    return chunks

