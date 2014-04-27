from datetime import datetime
import json
import unittest

from gaeutils.test import DatastoreTestCase
from mock import call
from mock import Mock
from mock import patch

from kaput import repository
from kaput.auth.user import User


@patch('kaput.repository.context')
class TestProcessRepoPush(unittest.TestCase):

    def test_fan_out(self, mock_context):
        """Ensure process_repo_push fans out tasks for each commit in the push
        data.
        """

        context = Mock()
        context.insert_success = 2
        mock_context.new.return_value.__enter__.return_value = context

        repo = Mock()
        repo_key = Mock()
        repo_key.id.return_value = 'repo'
        repo.key = repo_key
        owner = Mock()
        owner.github_token = 'token'
        commits = ['29fd6f4019d273bcac077d5f003623b8c78d8314',
                   '5575528bd903f296f835b9bd85be34b19ea8d6e1']
        data = {
            'ref': 'refs/heads/master',
            'after': '29fd6f4019d273bcac077d5f003623b8c78d8314',
            'before': '3f75528f4203f296f835b9bbeabe34b19ea8d420',
            'created': False,
            'deleted': False,
            'forced': False,
            'commits': [
                {
                    'id': '29fd6f4019d273bcac077d5f003623b8c78d8314',
                    'distinct': True,
                    'message': 'Add a new directory and file',
                    'timestamp': '2014-02-24T22:19:48-08:00',
                    'author': {
                        'name': 'Tyler Treat',
                        'email': 'ttreat31@gmail.com',
                        'username': 'tylertreat'
                    },
                    'committer': {
                        'name': 'Tyler Treat',
                        'email': 'ttreat31@gmail.com',
                        'username': 'tylertreat'
                    },
                    'added': [
                        'webhook_test/__init__.py'
                    ],
                    'removed': [],
                    'modified': []
                },
                {
                    'id': '5575528bd903f296f835b9bd85be34b19ea8d6e1',
                    'distinct': True,
                    'message': 'Add a new directory and file',
                    'timestamp': '2014-02-24T22:19:48-08:00',
                    'author': {
                        'name': 'Tyler Treat',
                        'email': 'ttreat31@gmail.com',
                        'username': 'tylertreat'
                    },
                    'committer': {
                        'name': 'Tyler Treat',
                        'email': 'ttreat31@gmail.com',
                        'username': 'tylertreat'
                    },
                    'added': [
                        'webhook_test/__init__.py'
                    ],
                    'removed': [],
                    'modified': []
                }
            ]
        }

        repository.process_repo_push(repo, owner, data)

        from kaput.repository import process_commit

        mock_context.new.assert_called_once_with()

        expected = [
            call(target=process_commit, args=(repo_key.id.return_value,
                                              commits[0],
                                              owner.key.id())),
            call(target=process_commit, args=(repo_key.id.return_value,
                                              commits[1],
                                              owner.key.id()))
        ]

        self.assertEqual(expected, context.add.call_args_list)


@patch('kaput.repository.ndb.put_multi')
@patch('kaput.repository.CommitHunk')
@patch('kaput.repository.Commit')
@patch('kaput.repository._get_commit')
@patch('kaput.repository.Repository.get_by_id')
@patch('kaput.repository.User.get_by_id')
class TestProcessCommit(unittest.TestCase):

    def test_process(self, mock_get_user, mock_get_repo, mock_get_commit,
                     mock_commit_init, mock_commit_hunk_init, mock_put_multi):
        """Ensure process_commit saves a Commit and CommitHunks to the
        datastore.
        """

        repo = repository.Repository(id=123, name='foo')
        mock_get_repo.return_value = repo

        mock_author = Mock()
        mock_author.id = 900
        mock_author.date = datetime.now()
        mock_author.name = 'Bruce Lee'
        mock_author.email = 'bruce@lee.com'

        mock_committer = Mock()
        mock_committer.id = 900
        mock_committer.date = datetime.now()
        mock_committer.name = 'Bruce Lee'
        mock_committer.email = 'bruce@lee.com'

        mock_commit_prop = Mock()
        mock_commit_prop.author = mock_author
        mock_commit_prop.committer = mock_committer
        mock_commit_prop.message = 'blah'
        mock_commit = Mock()
        mock_commit.commit = mock_commit_prop
        file1 = Mock()
        file1.filename = 'file1.py'
        file1.patch = '@@ -0,0 +1,4 @@ def main(): \n\n'
        file2 = Mock()
        file2.filename = 'file2.py'
        file2.patch = '@@ -14,4 +14,3 @@ def foo(bar): \n\n'
        mock_commit.files = [file1, file2]

        mock_author_user = Mock()
        mock_author_user.id = '123'
        mock_commit.author = mock_author
        mock_committer_user = Mock()
        mock_committer_user.id = '123'
        mock_commit.committer = mock_committer
        mock_get_commit.return_value = mock_commit

        commit = Mock()
        commit.key = Mock()
        commit.author_date = mock_author.date
        mock_commit_init.return_value = commit

        owner_token = 'token'
        user = User(id=123)
        user.github_token = owner_token
        mock_get_user.return_value = user

        commit_hunks = [Mock(), Mock()]
        mock_commit_hunk_init.side_effect = commit_hunks

        repo_id = '123'
        commit_id = 'abc'

        repository.process_commit(repo_id, commit_id, user.key.id())

        mock_get_repo.assert_called_once_with(repo_id)
        mock_get_commit.assert_called_once_with(repo.name, commit_id,
                                                owner_token)

        self.assertEqual([call(user.key.id()),
                          call('github_%s' % mock_author.id),
                          call('github_%s' % mock_committer.id)],
                         mock_get_user.call_args_list)

        mock_commit_init.assert_called_once_with(
            id=commit_id, repo=repo.key, sha=commit_id,
            author=user.key, author_name=mock_author.name,
            author_email=mock_author.email, author_date=mock_author.date,
            committer=user.key, committer_name=mock_committer.name,
            committer_email=mock_committer.email,
            committer_date=mock_committer.date,
            message=mock_commit_prop.message
        )

        mock_commit_init.return_value.put.assert_called_once_with()
        expected = [call(commit=commit.key,
                         filename='file1.py', lines=[1, 2, 3, 4],
                         timestamp=mock_author.date),
                    call(commit=commit.key,
                         filename='file2.py', lines=[14, 15, 16],
                         timestamp=mock_author.date)]
        self.assertEqual(expected, mock_commit_hunk_init.call_args_list)

        mock_put_multi.assert_called_once_with(commit_hunks)


@patch('kaput.repository.Github')
class TestGetCommit(unittest.TestCase):

    def test_get_commit(self, mock_github):
        """Ensure _get_commit returns a commit object for the correct repo."""

        github = Mock()
        mock_user = Mock()
        mock_repo = Mock()
        mock_commit = Mock()
        mock_repo.get_commit.return_value = mock_commit
        mock_user.get_repo.return_value = mock_repo
        github.get_user.return_value = mock_user
        mock_github.return_value = github

        repo_name = 'foo'
        commit_id = 'abc'
        owner_token = 'token'

        actual = repository._get_commit(repo_name, commit_id, owner_token)

        mock_github.assert_called_once_with(owner_token)
        github.get_user.assert_called_once_with()
        mock_user.get_repo.assert_called_once_with(repo_name)
        mock_repo.get_commit.assert_called_once_with(commit_id)
        self.assertEqual(mock_commit, actual)


@patch('kaput.repository.memcache.set')
@patch('kaput.repository.Repository')
@patch('kaput.repository.ndb')
class TestSyncRepos(unittest.TestCase):

    def test_sync(self, mock_ndb, mock_repo, mock_set):
        """Ensure that a Repository entity is created for every GitHub repo
        that doesn't already have an entity and a list of the user's repos is
        returned.
        """

        mock_user = Mock()
        repo1 = Mock()
        repo1.id = 'repo1'
        repo2 = Mock()
        repo2.id = 'repo2'
        repo2.name = 'repo2'
        repo2.description = 'description'
        mock_user.github_repos = [repo1, repo2]
        key1 = Mock()
        key2 = Mock()
        keys = [key1, key2]
        mock_ndb.Key.side_effect = keys
        mock_ndb.get_multi.return_value = [repo1, None]

        actual = repository.sync_repos(mock_user)

        self.assertEqual([repo1, mock_repo.return_value], actual)
        expected = [call(User, mock_user.key.id(), repository.Repository,
                         'github_%s' % repo.id)
                    for repo in [repo1, repo2]]
        self.assertEqual(expected, mock_ndb.Key.call_args_list)
        mock_ndb.get_multi.assert_called_once_with(keys)
        mock_repo.assert_called_once_with(id='github_%s' % repo2.id,
                                          description=repo2.description,
                                          name=repo2.name, owner=mock_user.key)
        mock_ndb.put_multi.assert_called_once_with([mock_repo.return_value])
        mock_set.assert_called_once_with(
            'kaput:repos:%s' % mock_user.key.id(),
            [repo1, mock_repo.return_value])


class TestEnableRepo(DatastoreTestCase):

    def test_enable(self):
        """Ensure that when a Repository is enabled, the entity is updated and
        the webhook is created.
        """

        mock_repo = Mock()
        mock_repo.enabled = False

        repository.enable_repo(mock_repo, True)

        self.assertTrue(mock_repo.enabled)
        mock_repo.put.assert_called_once_with()
        mock_repo.create_webhooks.assert_called_once_with()

    def test_disable(self):
        """Ensure that when a Repository is disabled, the entity is updated and
        the webhook is deleted.
        """

        mock_repo = Mock()
        mock_repo.enabled = True

        repository.enable_repo(mock_repo, False)

        self.assertFalse(mock_repo.enabled)
        mock_repo.put.assert_called_once_with()
        mock_repo.delete_webhooks.assert_called_once_with()


@patch('kaput.repository.settings')
class TestRepository(unittest.TestCase):

    def setUp(self):
        self.name = 'foo'
        self.description = 'foo bar baz'
        self.owner = User(username='user', emails=['email'],
                          primary_email='email', github_token='token')
        self.repo = repository.Repository(name=self.name,
                                          description=self.description,
                                          owner=self.owner.key)

    @patch('kaput.repository.gh.get_webhooks')
    def test_get_webhooks(self, mock_get_hooks, mock_settings):
        """Ensure that the Kaput webhooks are returned."""

        mock_settings.PUSH_WEBHOOK_URI = 'http://localhost:8080/push'
        mock_settings.RELEASE_WEBHOOK_URI = 'http://localhost:8080/release'

        actual = self.repo.get_webhooks()

        self.assertEqual(mock_get_hooks.return_value, actual)

    @patch('kaput.repository.gh.create_webhook')
    def test_create_webhooks(self, mock_create_hook, mock_settings):
        """Ensure that the Kaput webhook is created."""

        mock_settings.PUSH_WEBHOOK_URI = 'http://localhost:8080/push'
        mock_settings.RELEASE_WEBHOOK_URI = 'http://localhost:8080/release'

        actual = self.repo.create_webhooks()

        self.assertTrue(actual)
        expected = [call(self.repo, mock_settings.PUSH_WEBHOOK_URI),
                    call(self.repo, mock_settings.RELEASE_WEBHOOK_URI,
                         events=['release'])]
        self.assertEqual(expected, mock_create_hook.call_args_list)

    @patch('kaput.repository.gh.delete_webhook')
    def test_delete_webhook(self, mock_delete_hook, mock_settings):
        """Ensure that the Kaput webhooks are deleted."""

        mock_settings.PUSH_WEBHOOK_URI = 'http://localhost:8080/push'
        mock_settings.RELEASE_WEBHOOK_URI = 'http://localhost:8080/release'

        self.repo.delete_webhooks()

        expected = [call(self.repo, mock_settings.PUSH_WEBHOOK_URI),
                    call(self.repo, mock_settings.RELEASE_WEBHOOK_URI)]
        self.assertEqual(expected, mock_delete_hook.call_args_list)


@patch('kaput.repository.Repository.get_by_id')
class TestProcessRelease(unittest.TestCase):

    def setUp(self):
        self.repo_id = 123
        self.release_json = """{
            "url": "url",
            "assets_url": "assets url",
            "upload_url": "upload url",
            "html_url": "html url",
            "id": 286074,
            "tag_name": "v0.0.3",
            "target_commitish": "master",
            "name": "This is a test release",
            "draft": false,
            "author": {
                "login": "tylertreat",
                "id": 552817,
                "avatar_url": "avatar url",
                "gravatar_id": "dcbf01e42178cd9698fb3d4806e33d84",
                "url": "https://api.github.com/users/tylertreat",
                "html_url": "https://github.com/tylertreat",
                "followers_url": "followers url",
                "following_url": "following url",
                "gists_url": "gists url",
                "starred_url": "starred url",
                "subscriptions_url": "subscriptions url",
                "organizations_url": "organizations url",
                "repos_url": "https://api.github.com/users/tylertreat/repos",
                "events_url": "events url",
                "received_events_url": "received events url",
                "type": "User",
                "site_admin": false
            },
            "prerelease": false,
            "created_at": "2014-04-24T03:51:08Z",
            "published_at": "2014-04-24T03:54:53Z",
            "assets": [],
            "tarball_url": "tarball url",
            "zipball_url": "zipball url",
            "body": ""
        }"""
        self.release_data = json.loads(self.release_json)

    def test_no_repo(self, mock_get):
        """Ensure that if the Repository doesn't exist, an exception is raised.
        """

        mock_get.return_value = None

        self.assertRaises(Exception, repository.process_release, self.repo_id,
                          self.release_data)
        mock_get.assert_called_once_with('github_%s' % self.repo_id)

    @patch('kaput.repository._tag_commits')
    @patch('kaput.repository.Release')
    def test_fan_out(self, mock_release, mock_tag, mock_get):
        """Ensure that a Release entity is created and saved and that tasks
        are inserted for tagging commits with the release.
        """

        mock_repo = Mock()
        mock_get.return_value = mock_repo

        actual = repository.process_release(self.repo_id, self.release_data)

        self.assertEqual(mock_release.return_value, actual)
        mock_release.assert_called_once_with(
            id='github_%s' % self.release_data['id'],
            parent=mock_repo.key,
            tag_name=self.release_data['tag_name'],
            name=self.release_data['name'],
            description=self.release_data['body'],
            prerelease=self.release_data['prerelease'],
            created=datetime.strptime(self.release_data['created_at'],
                                      '%Y-%m-%dT%H:%M:%SZ'),
            published=datetime.strptime(self.release_data['published_at'],
                                        '%Y-%m-%dT%H:%M:%SZ'),
            url=self.release_data['html_url'])
        mock_release.return_value.put.assert_called_once_with()
        mock_tag.assert_called_once_with(mock_repo, mock_release.return_value)

