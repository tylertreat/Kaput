import unittest

from mock import call
from mock import Mock
from mock import patch

from kaput import backfill


@patch('kaput.backfill.Repository.get_by_id')
@patch('kaput.backfill.CommitData')
@patch('kaput.backfill.populate_commit')
@patch('kaput.backfill.AutoContext')
@patch('kaput.backfill.gh.get_commits')
class TestBackfillRepo(unittest.TestCase):

    def test_fan_out(self, mock_get_commits, mock_context, mock_populate,
                     mock_commit_data, mock_get_repo):
        """Ensure that a backfill task is inserted for each commit."""

        context = Mock()
        mock_context.return_value.__enter__.return_value = context
        commit1 = Mock()
        commit2 = Mock()
        mock_get_commits.return_value = [commit1, commit2]
        commit_data1 = Mock()
        commit_data2 = Mock()
        mock_commit_data.side_effect = [commit_data1, commit_data2]
        repo = Mock()
        mock_get_repo.return_value = repo

        repo_id = 123

        backfill.backfill_repo(repo_id)

        mock_get_commits.assert_called_once_with(repo)
        mock_context.assert_called_once_with(batch_size=100)

        calls = [call(data=commit1.raw_data), call(data=commit2.raw_data)]
        self.assertEqual(calls, mock_commit_data.call_args_list)

        calls = [call(target=backfill.backfill_commit,
                      args=(repo.key.id(), commit_data1.key.id())),
                 call(target=backfill.backfill_commit,
                      args=(repo.key.id(), commit_data2.key.id()))]
        self.assertEqual(calls, context.add.call_args_list)


@patch('kaput.backfill.Commit.get_by_id')
@patch('kaput.backfill.populate_commit')
@patch('kaput.backfill.Github')
@patch('kaput.backfill.CommitData.get_by_id')
@patch('kaput.backfill.Repository.get_by_id')
class TestBackfillCommit(unittest.TestCase):

    def test_backfill(self, mock_get_repo, mock_get_commit_data, mock_github,
                      mock_populate, mock_get_commit):
        """Ensure that populate_commit is called for the specified commit when
        a Commit entity doesn't exist for it.
        """
        from github.Commit import Commit

        commit = Mock()
        mock_github.return_value.create_from_raw_data.return_value = commit
        mock_get_commit.return_value = None

        repo_id = 123
        commit_data_id = 456

        backfill.backfill_commit(repo_id, commit_data_id)

        mock_get_repo.assert_called_once_with(repo_id)
        mock_get_commit_data.assert_called_once_with(commit_data_id)
        mock_github.return_value.create_from_raw_data.assert_called_once_with(
            Commit, mock_get_commit_data.return_value.data)
        mock_populate.assert_called_once_with(
            commit, mock_get_repo.return_value)
        mock_get_commit_data.return_value.key.delete.assert_called_once_with()
        mock_get_commit.assert_called_once_with(
            commit.sha, parent=mock_get_repo.return_value.key)

    def test_idempotent(self, mock_get_repo, mock_get_commit_data, mock_github,
                        mock_populate, mock_get_commit):
        """Ensure that populate_commit is not called for the specified commit
        when a Commit entity already exists for it.
        """
        from furious.errors import Abort
        from github.Commit import Commit

        commit = Mock()
        mock_github.return_value.create_from_raw_data.return_value = commit

        repo_id = 123
        commit_data_id = 456

        self.assertRaises(Abort, backfill.backfill_commit, repo_id,
                          commit_data_id)

        mock_get_repo.assert_called_once_with(repo_id)
        mock_get_commit_data.assert_called_once_with(commit_data_id)
        mock_github.return_value.create_from_raw_data.assert_called_once_with(
            Commit, mock_get_commit_data.return_value.data)
        self.assertFalse(mock_populate.called)
        mock_get_commit_data.return_value.key.delete.assert_called_once_with()
        mock_get_commit.assert_called_once_with(
            commit.sha, parent=mock_get_repo.return_value.key)

