import json
import os
import uuid

from datetime import datetime
from furious.test_stubs.appengine.queues import run as run_queues
from gaeutils.test import DatastoreMemcacheTestCase
from google.appengine.ext import testbed
from mock import patch
from nose.plugins.attrib import attr

from kaput.api import controller
from kaput.auth.user import User
from kaput.repository import Repository


@attr('slow')
@patch('kaput.repository._get_commit')
@patch('kaput.api.controller.request')
@patch('kaput.api.controller._verify_webhook_origin')
class TestProcessGithubPush(DatastoreMemcacheTestCase):

    def setUp(self):
        from github import Github
        from github.Commit import Commit
        from kaput.tests import KAPUT_QUEUES_PATH

        super(TestProcessGithubPush, self).setUp()
        self.testbed.init_taskqueue_stub(root_path=KAPUT_QUEUES_PATH)

        # Ensure each test looks like a new request.
        os.environ['REQUEST_ID_HASH'] = uuid.uuid4().hex

        self.queue_service = self.testbed.get_stub(
            testbed.TASKQUEUE_SERVICE_NAME)

        self.user = User(id='github_123', username='tylertreat',
                         primary_email='ttreat31@gmail.com',
                         emails=['ttreat31@gmail.com'],
                         github_token='token')
        self.user.put()

        self.push_payload = """
        {
            "ref": "refs/heads/master",
            "after": "0832d0f7deb197617c9cdafd318432fc13bee35d",
            "before": "41b5ac93f2b4bdf655050146e108af3c399753e5",
            "created": false,
            "deleted": false,
            "forced": false,
            "compare": "https://github.com/tylertreat/webhook-test/compare/41b5ac93f2b4...0832d0f7deb1",
            "commits": [
                {
                    "id": "0832d0f7deb197617c9cdafd318432fc13bee35d",
                    "distinct": true,
                    "message": "Delete another newline",
                    "timestamp": "2014-05-26T00:12:09-05:00",
                    "url": "https://github.com/tylertreat/webhook-test/commit/0832d0f7deb197617c9cdafd318432fc13bee35d",
                    "author": {
                        "name": "Tyler Treat",
                        "email": "ttreat31@gmail.com",
                        "username": "tylertreat"
                    },
                    "committer": {
                        "name": "Tyler Treat",
                        "email": "ttreat31@gmail.com",
                        "username": "tylertreat"
                    },
                    "added": [],
                    "removed": [],
                    "modified": [
                        "main.py"
                    ]
                }
            ],
            "head_commit": {
                "id": "0832d0f7deb197617c9cdafd318432fc13bee35d",
                "distinct": true,
                "message": "Delete another newline",
                "timestamp": "2014-05-26T00:12:09-05:00",
                "url": "https://github.com/tylertreat/webhook-test/commit/0832d0f7deb197617c9cdafd318432fc13bee35d",
                "author": {
                    "name": "Tyler Treat",
                    "email": "ttreat31@gmail.com",
                    "username": "tylertreat"
                },
                "committer": {
                    "name": "Tyler Treat",
                    "email": "ttreat31@gmail.com",
                    "username": "tylertreat"
                },
                "added": [],
                "removed": [],
                "modified": [
                    "main.py"
                ]
            },
            "repository": {
                "id": 16896925,
                "name": "webhook-test",
                "url": "https://github.com/tylertreat/webhook-test",
                "description": "webhook test",
                "watchers": 0,
                "stargazers": 0,
                "forks": 0,
                "fork": false,
                "size": 1048,
                "owner": {
                    "name": "tylertreat",
                    "email": "ttreat31@gmail.com"
                },
                "private": false,
                "open_issues": 0,
                "has_issues": true,
                "has_downloads": true,
                "has_wiki": true,
                "language": "Python",
                "created_at": 1392593853,
                "pushed_at": 1401081153,
                "master_branch": "master"
            },
            "pusher": {
                "name": "tylertreat",
                "email": "ttreat31@gmail.com"
            }
        }
        """

        github = Github()
        self.commit = github.create_from_raw_data(Commit, json.loads(
            r'''
            {
                "sha": "0832d0f7deb197617c9cdafd318432fc13bee35d",
                "commit": {
                    "author": {
                        "name": "Tyler Treat",
                        "email": "ttreat31@gmail.com",
                        "date": "2014-05-26T05:12:09Z"
                    },
                    "committer": {
                        "name": "Tyler Treat",
                        "email": "ttreat31@gmail.com",
                        "date": "2014-05-26T05:12:09Z"
                    },
                    "message": "Delete another newline",
                    "tree": {
                        "sha": "60e97a797de99d0d8a8a1ca05399145f14f98a66",
                        "url": "https://api.github.com/repos/tylertreat/webhook-test/git/trees/60e97a797de99d0d8a8a1ca05399145f14f98a66"
                    },
                    "url": "https://api.github.com/repos/tylertreat/webhook-test/git/commits/0832d0f7deb197617c9cdafd318432fc13bee35d",
                    "comment_count": 0
                },
                "url": "https://api.github.com/repos/tylertreat/webhook-test/commits/0832d0f7deb197617c9cdafd318432fc13bee35d",
                "html_url": "https://github.com/tylertreat/webhook-test/commit/0832d0f7deb197617c9cdafd318432fc13bee35d",
                "comments_url": "https://api.github.com/repos/tylertreat/webhook-test/commits/0832d0f7deb197617c9cdafd318432fc13bee35d/comments",
                "author": {
                    "login": "tylertreat",
                    "id": 552817,
                    "avatar_url": "https://avatars.githubusercontent.com/u/552817?",
                    "gravatar_id": "dcbf01e42178cd9698fb3d4806e33d84",
                    "url": "https://api.github.com/users/tylertreat",
                    "html_url": "https://github.com/tylertreat",
                    "followers_url": "https://api.github.com/users/tylertreat/followers",
                    "following_url": "https://api.github.com/users/tylertreat/following{/other_user}",
                    "gists_url": "https://api.github.com/users/tylertreat/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/tylertreat/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/tylertreat/subscriptions",
                    "organizations_url": "https://api.github.com/users/tylertreat/orgs",
                    "repos_url": "https://api.github.com/users/tylertreat/repos",
                    "events_url": "https://api.github.com/users/tylertreat/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/tylertreat/received_events",
                    "type": "User",
                    "site_admin": false
                },
                "committer": {
                    "login": "tylertreat",
                    "id": 552817,
                    "avatar_url": "https://avatars.githubusercontent.com/u/552817?",
                    "gravatar_id": "dcbf01e42178cd9698fb3d4806e33d84",
                    "url": "https://api.github.com/users/tylertreat",
                    "html_url": "https://github.com/tylertreat",
                    "followers_url": "https://api.github.com/users/tylertreat/followers",
                    "following_url": "https://api.github.com/users/tylertreat/following{/other_user}",
                    "gists_url": "https://api.github.com/users/tylertreat/gists{/gist_id}",
                    "starred_url": "https://api.github.com/users/tylertreat/starred{/owner}{/repo}",
                    "subscriptions_url": "https://api.github.com/users/tylertreat/subscriptions",
                    "organizations_url": "https://api.github.com/users/tylertreat/orgs",
                    "repos_url": "https://api.github.com/users/tylertreat/repos",
                    "events_url": "https://api.github.com/users/tylertreat/events{/privacy}",
                    "received_events_url": "https://api.github.com/users/tylertreat/received_events",
                    "type": "User",
                    "site_admin": false
                },
                "parents": [
                    {
                        "sha": "a4240c12ef6152503ab6be1d80f9fbae4609d572",
                        "url": "https://api.github.com/repos/tylertreat/webhook-test/commits/a4240c12ef6152503ab6be1d80f9fbae4609d572",
                        "html_url": "https://github.com/tylertreat/webhook-test/commit/a4240c12ef6152503ab6be1d80f9fbae4609d572"
                    }
                ],
                "stats": {
                    "total": 1,
                    "additions": 0,
                    "deletions": 1
                },
                "files": [
                    {
                        "sha": "8e32958cd62fb81a7548c46327baead0e8816156",
                        "filename": "main.py",
                        "status": "modified",
                        "additions": 0,
                        "deletions": 1,
                        "changes": 1,
                        "blob_url": "https://github.com/tylertreat/webhook-test/blob/0832d0f7deb197617c9cdafd318432fc13bee35d/main.py",
                        "raw_url": "https://github.com/tylertreat/webhook-test/raw/0832d0f7deb197617c9cdafd318432fc13bee35d/main.py",
                        "contents_url": "https://api.github.com/repos/tylertreat/webhook-test/contents/main.py?ref=0832d0f7deb197617c9cdafd318432fc13bee35d",
                        "patch": "@@ -35,4 +35,3 @@ def push():\n \n if __name__ == '__main__':\n     app.run()\n-"
                    }
                ]
            }
            '''
        ))

    def test_happy_path(self, mock_verify_origin, mock_request,
                        mock_get_commit):
        """Ensure process_github_push creates Commit and CommitHunk entities.
        """
        from kaput.repository import Commit
        from kaput.repository import CommitHunk

        mock_verify_origin.return_value = True
        mock_request.data = self.push_payload
        mock_get_commit.return_value = self.commit

        repo = Repository(id='github_16896925', name='webhook-test',
                          description='webhook test', owner=self.user.key,
                          enabled=True)
        repo.put()

        commit = Commit.get_by_id(self.commit.sha, parent=repo.key)
        self.assertIsNone(commit)

        controller.process_github_push()
        run_queues(self.queue_service)

        commit = Commit.get_by_id(self.commit.sha, parent=repo.key)
        self.assertEqual(repo.key, commit.key.parent())
        self.assertIsNone(commit.author)
        self.assertEqual('Tyler Treat', commit.author_name)
        self.assertEqual('ttreat31@gmail.com', commit.author_email)
        self.assertEqual(datetime(2014, 5, 26, 5, 12, 9), commit.author_date)
        self.assertIsNone(commit.committer)
        self.assertEqual('Tyler Treat', commit.committer_name)
        self.assertEqual('ttreat31@gmail.com', commit.committer_email)
        self.assertEqual(datetime(2014, 5, 26, 5, 12, 9),
                         commit.committer_date)
        self.assertEqual('Delete another newline', commit.message)

        hunks = CommitHunk.query(ancestor=commit.key).fetch()
        self.assertEqual(1, len(hunks))
        hunk = hunks[0]
        self.assertEqual(commit.key, hunk.key.parent())
        self.assertEqual(commit.key, hunk.commit)
        self.assertEqual('main.py', hunk.filename)
        self.assertEqual([35, 36, 37], hunk.lines)
        self.assertEqual(datetime(2014, 5, 26, 5, 12, 9), hunk.timestamp)

