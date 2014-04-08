from datetime import datetime
import unittest

from mock import call
from mock import Mock
from mock import patch

from kaput import repository


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
        owner.github_access_token = 'token'
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
                                              owner.github_access_token)),
            call(target=process_commit, args=(repo_key.id.return_value,
                                              commits[1],
                                              owner.github_access_token))
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
        from kaput.user import User

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

        user = User(id=123)
        mock_get_user.return_value = user

        commit_hunks = [Mock(), Mock()]
        mock_commit_hunk_init.side_effect = commit_hunks

        repo_id = '123'
        commit_id = 'abc'
        owner_token = 'token'

        repository.process_commit(repo_id, commit_id, owner_token)

        mock_get_repo.assert_called_once_with(repo_id)
        mock_get_commit.assert_called_once_with(repo.name, commit_id,
                                                owner_token)

        self.assertEqual([call('github_%s' % mock_author.id),
                          call('github_%s' % mock_committer.id)],
                         mock_get_user.call_args_list)

        mock_commit_init.assert_called_once_with(
            id=commit_id, parent=repo.key, repo=repo.key, sha=commit_id,
            author=user.key, author_name=mock_author.name,
            author_email=mock_author.email, author_date=mock_author.date,
            committer=user.key, committer_name=mock_committer.name,
            committer_email=mock_committer.email,
            committer_date=mock_committer.date,
            message=mock_commit_prop.message
        )

        mock_commit_init.return_value.put.assert_called_once_with()
        expected = [call(parent=commit.key, commit=commit.key,
                         filename='file1.py', lines=[1, 2, 3, 4],
                         timestamp=mock_author.date),
                    call(parent=commit.key, commit=commit.key,
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


@patch('kaput.repository.Repository')
@patch('kaput.repository.ndb')
@patch('kaput.repository.User.get_by_id')
class TestSyncRepos(unittest.TestCase):

    def test_sync(self, mock_get_by_id, mock_ndb, mock_repo):
        """Ensure that a Repository entity is created for every GitHub repo
        that doesn't already have an entity and the list of created entities is
        returned.
        """

        mock_user = Mock()
        repo1 = Mock()
        repo1.id = 'repo1'
        repo2 = Mock()
        repo2.id = 'repo2'
        repo2.name = 'repo2'
        mock_user.get_github_repos.return_value = [repo1, repo2]
        mock_get_by_id.return_value = mock_user
        key1 = Mock()
        key2 = Mock()
        keys = [key1, key2]
        mock_ndb.Key.side_effect = keys
        mock_ndb.get_multi.return_value = [repo1, None]
        user_id = '123'

        actual = repository.sync_repos(user_id)

        self.assertEqual([mock_repo.return_value], actual)
        mock_get_by_id.assert_called_once_with(user_id)
        mock_user.get_github_repos.assert_called_once_with()
        expected = [call(repository.Repository, 'github_%s' % repo.id)
                    for repo in [repo1, repo2]]
        self.assertEqual(expected, mock_ndb.Key.call_args_list)
        mock_ndb.get_multi.assert_called_once_with(keys)
        mock_repo.assert_called_once_with(id='github_%s' % repo2.id,
                                          name=repo2.name, owner=mock_user.key)
        mock_ndb.put_multi.assert_called_once_with([mock_repo.return_value])

