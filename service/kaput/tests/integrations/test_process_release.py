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
@patch('kaput.api.controller.request')
@patch('kaput.api.controller._verify_webhook_origin')
class TestProcessGithubRelease(DatastoreMemcacheTestCase):

    def setUp(self):
        from kaput.tests import KAPUT_QUEUES_PATH

        super(TestProcessGithubRelease, self).setUp()
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

        self.release_payload = """
        {
            "action": "published",
            "release": {
                "url": "https://api.github.com/repos/tylertreat/webhook-test/releases/339538",
                "assets_url": "https://api.github.com/repos/tylertreat/webhook-test/releases/339538/assets",
                "upload_url": "https://uploads.github.com/repos/tylertreat/webhook-test/releases/339538/assets{?name}",
                "html_url": "https://github.com/tylertreat/webhook-test/releases/tag/v0.0.4",
                "id": 339538,
                "tag_name": "v0.0.4",
                "target_commitish": "master",
                "name": "Another Test Release",
                "draft": false,
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
                "prerelease": false,
                "created_at": "2014-05-26T05:12:09Z",
                "published_at": "2014-05-26T05:14:46Z",
                "assets": [

                ],
                "tarball_url": "https://api.github.com/repos/tylertreat/webhook-test/tarball/v0.0.4",
                "zipball_url": "https://api.github.com/repos/tylertreat/webhook-test/zipball/v0.0.4",
                "body": "Testing 123"
            },
            "repository": {
                "id": 16896925,
                "name": "webhook-test",
                "full_name": "tylertreat/webhook-test",
                "owner": {
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
                "private": false,
                "html_url": "https://github.com/tylertreat/webhook-test",
                "description": "webhook test",
                "fork": false,
                "url": "https://api.github.com/repos/tylertreat/webhook-test",
                "forks_url": "https://api.github.com/repos/tylertreat/webhook-test/forks",
                "keys_url": "https://api.github.com/repos/tylertreat/webhook-test/keys{/key_id}",
                "collaborators_url": "https://api.github.com/repos/tylertreat/webhook-test/collaborators{/collaborator}",
                "teams_url": "https://api.github.com/repos/tylertreat/webhook-test/teams",
                "hooks_url": "https://api.github.com/repos/tylertreat/webhook-test/hooks",
                "issue_events_url": "https://api.github.com/repos/tylertreat/webhook-test/issues/events{/number}",
                "events_url": "https://api.github.com/repos/tylertreat/webhook-test/events",
                "assignees_url": "https://api.github.com/repos/tylertreat/webhook-test/assignees{/user}",
                "branches_url": "https://api.github.com/repos/tylertreat/webhook-test/branches{/branch}",
                "tags_url": "https://api.github.com/repos/tylertreat/webhook-test/tags",
                "blobs_url": "https://api.github.com/repos/tylertreat/webhook-test/git/blobs{/sha}",
                "git_tags_url": "https://api.github.com/repos/tylertreat/webhook-test/git/tags{/sha}",
                "git_refs_url": "https://api.github.com/repos/tylertreat/webhook-test/git/refs{/sha}",
                "trees_url": "https://api.github.com/repos/tylertreat/webhook-test/git/trees{/sha}",
                "statuses_url": "https://api.github.com/repos/tylertreat/webhook-test/statuses/{sha}",
                "languages_url": "https://api.github.com/repos/tylertreat/webhook-test/languages",
                "stargazers_url": "https://api.github.com/repos/tylertreat/webhook-test/stargazers",
                "contributors_url": "https://api.github.com/repos/tylertreat/webhook-test/contributors",
                "subscribers_url": "https://api.github.com/repos/tylertreat/webhook-test/subscribers",
                "subscription_url": "https://api.github.com/repos/tylertreat/webhook-test/subscription",
                "commits_url": "https://api.github.com/repos/tylertreat/webhook-test/commits{/sha}",
                "git_commits_url": "https://api.github.com/repos/tylertreat/webhook-test/git/commits{/sha}",
                "comments_url": "https://api.github.com/repos/tylertreat/webhook-test/comments{/number}",
                "issue_comment_url": "https://api.github.com/repos/tylertreat/webhook-test/issues/comments/{number}",
                "contents_url": "https://api.github.com/repos/tylertreat/webhook-test/contents/{+path}",
                "compare_url": "https://api.github.com/repos/tylertreat/webhook-test/compare/{base}...{head}",
                "merges_url": "https://api.github.com/repos/tylertreat/webhook-test/merges",
                "archive_url": "https://api.github.com/repos/tylertreat/webhook-test/{archive_format}{/ref}",
                "downloads_url": "https://api.github.com/repos/tylertreat/webhook-test/downloads",
                "issues_url": "https://api.github.com/repos/tylertreat/webhook-test/issues{/number}",
                "pulls_url": "https://api.github.com/repos/tylertreat/webhook-test/pulls{/number}",
                "milestones_url": "https://api.github.com/repos/tylertreat/webhook-test/milestones{/number}",
                "notifications_url": "https://api.github.com/repos/tylertreat/webhook-test/notifications{?since,all,participating}",
                "labels_url": "https://api.github.com/repos/tylertreat/webhook-test/labels{/name}",
                "releases_url": "https://api.github.com/repos/tylertreat/webhook-test/releases{/id}",
                "created_at": "2014-02-16T23:37:33Z",
                "updated_at": "2014-05-26T05:12:31Z",
                "pushed_at": "2014-05-26T05:14:46Z",
                "git_url": "git://github.com/tylertreat/webhook-test.git",
                "ssh_url": "git@github.com:tylertreat/webhook-test.git",
                "clone_url": "https://github.com/tylertreat/webhook-test.git",
                "svn_url": "https://github.com/tylertreat/webhook-test",
                "homepage": null,
                "size": 1048,
                "stargazers_count": 0,
                "watchers_count": 0,
                "language": "Python",
                "has_issues": true,
                "has_downloads": true,
                "has_wiki": true,
                "forks_count": 0,
                "mirror_url": null,
                "open_issues_count": 0,
                "forks": 0,
                "open_issues": 0,
                "watchers": 0,
                "default_branch": "master"
            },
            "sender": {
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
            }
        }
        """

    def test_happy_path(self, mock_verify_origin, mock_request):
        """Ensure that process_github_release creates a Release entity and
        correctly tags Commits.
        """
        from kaput.repository import Commit
        from kaput.repository import Release

        mock_verify_origin.return_value = True
        mock_request.data = self.release_payload

        repo = Repository(id='github_16896925', name='webhook-test',
                          description='webhook test', owner=self.user.key,
                          enabled=True)
        repo.put()

        old_release = Release(id='github_123', parent=repo.key,
                              tag_name='v0.0.1', name='release', url='url',
                              description='description', prerelease=False,
                              created=datetime.utcnow(),
                              published=datetime.utcnow())
        old_release.put()

        tagged_commit = Commit(id='abc', parent=repo.key, sha='abc',
                               author_name='Tyler Treat',
                               author_email='ttreat31@gmail.com',
                               author_date=datetime.utcnow(),
                               committer_name='Tyler Treat',
                               committer_email='ttreat31@gmail.com',
                               committer_date=datetime.utcnow(),
                               release=old_release.key)
        tagged_commit.put()

        untagged_commit = Commit(id='def', parent=repo.key, sha='def',
                                 author_name='Tyler Treat',
                                 author_email='ttreat31@gmail.com',
                                 author_date=datetime.utcnow(),
                                 committer_name='Tyler Treat',
                                 committer_email='ttreat31@gmail.com',
                                 committer_date=datetime.utcnow())
        untagged_commit.put()

        controller.process_github_release()
        run_queues(self.queue_service)

        release = Release.get_by_id('github_339538', parent=repo.key)

        self.assertEqual(repo.key, release.key.parent())
        self.assertEqual('github_339538', release.key.id())
        self.assertEqual('v0.0.4', release.tag_name)
        self.assertEqual('Another Test Release', release.name)
        self.assertEqual('Testing 123', release.description)
        self.assertFalse(release.prerelease)
        self.assertEqual(datetime(2014, 5, 26, 5, 12, 9), release.created)
        self.assertEqual(datetime(2014, 5, 26, 5, 14, 46), release.published)
        self.assertEqual(
            'https://github.com/tylertreat/webhook-test/releases/tag/v0.0.4',
            release.url
        )

        commits = Commit.query().fetch()
        self.assertEqual(2, len(commits))
        self.assertEqual(old_release.key, commits[0].release)
        self.assertEqual(release.key, commits[1].release)

