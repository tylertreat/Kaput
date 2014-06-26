import logging

from furious.async import defaults
from furious.context.auto_context import AutoContext
from github import Github
from github.Commit import Commit
from google.appengine.ext import ndb

from kaput.repository import COMMIT_QUEUE
from kaput.repository import populate_commit
from kaput.repository import Repository
from kaput.services import gh


class CommitData(ndb.Model):
    data = ndb.JsonProperty(compressed=True)


def backfill_repo(repo):
    """Create Commit and CommitHunk entities for all commits up to now which do
    not already have entities created. For example, this allows commits made
    before a repo is added to Kaput to be included.

    Args:
        repo: the Repository to backfill.
    """

    commits = gh.get_commits(repo)
    logging.debug('Backfilling commits for %s' % repo)

    # TODO: This won't scale well...
    with AutoContext(batch_size=100) as ctx:
        for commit in commits:
            commit_data = CommitData(data=commit.raw_data)
            commit_data.put()
            ctx.add(target=backfill_commit, args=(repo.key.id(),
                                                  commit_data.key.id()))


@defaults(queue=COMMIT_QUEUE)
def backfill_commit(repo_id, commit_data_id):
    repo = Repository.get_by_id(repo_id)
    commit_data = CommitData.get_by_id(commit_data_id)
    commit = Github().create_from_raw_data(Commit, commit_data.data)
    populate_commit(commit, repo)
    commit_data.key.delete()

