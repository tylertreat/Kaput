import unittest

from mock import Mock
from mock import patch

from kaput import blame
from kaput.repository import CommitHunk


@patch('kaput.blame.CommitHunk.query')
class TestBlame(unittest.TestCase):

    def test_no_hunk(self, mock_query):
        """Ensure that when no CommitHunk is found, None is returned."""

        first_query = Mock()
        second_query = Mock()
        third_query = Mock()
        fourth_query = Mock()

        first_query.filter.return_value = second_query
        second_query.filter.return_value = third_query
        third_query.order.return_value = fourth_query
        fourth_query.get.return_value = None
        mock_query.return_value = first_query

        repo = Mock()
        repo.key = Mock()
        filename = 'foo'
        line_number = 5

        name, email, user = blame.blame(repo, filename, line_number)

        self.assertIsNone(name)
        self.assertIsNone(email)
        self.assertIsNone(user)
        mock_query.assert_called_once_with(ancestor=repo.key)
        first_query.filter.assert_called_once_with(
            CommitHunk.filename == filename)
        second_query.filter.assert_called_once_with(
            CommitHunk.lines == line_number)
        third_query.order.assert_called_once_with(-CommitHunk.timestamp)
        fourth_query.get.assert_called_once_with()

    def test_user_exists(self, mock_query):
        """Ensure that the corrent name, email and User are returned when the
        User exists.
        """

        first_query = Mock()
        second_query = Mock()
        third_query = Mock()
        fourth_query = Mock()
        hunk_key = Mock()
        commit_hunk = Mock()
        commit_hunk.key = hunk_key
        commit = Mock()
        commit.author_name = 'Bruce Lee'
        commit.author_email = 'bruce@lee.com'
        author_key = Mock()
        author = Mock()
        author_key.get.return_value = author
        commit.author = author_key
        hunk_key.parent.return_value.get.return_value = commit

        first_query.filter.return_value = second_query
        second_query.filter.return_value = third_query
        third_query.order.return_value = fourth_query
        fourth_query.get.return_value = commit_hunk
        mock_query.return_value = first_query

        repo = Mock()
        repo.key = Mock()
        filename = 'foo'
        line_number = 5

        name, email, user = blame.blame(repo, filename, line_number)

        self.assertEqual(commit.author_name, name)
        self.assertEqual(commit.author_email, email)
        self.assertEqual(author, user)
        mock_query.assert_called_once_with(ancestor=repo.key)
        first_query.filter.assert_called_once_with(
            CommitHunk.filename == filename)
        second_query.filter.assert_called_once_with(
            CommitHunk.lines == line_number)
        third_query.order.assert_called_once_with(-CommitHunk.timestamp)
        fourth_query.get.assert_called_once_with()

    def test_user_does_not_exist(self, mock_query):
        """Ensure that the corrent name, email and None are returned when the
        User does not exist.
        """

        first_query = Mock()
        second_query = Mock()
        third_query = Mock()
        fourth_query = Mock()
        hunk_key = Mock()
        commit_hunk = Mock()
        commit_hunk.key = hunk_key
        commit = Mock()
        commit.author_name = 'Bruce Lee'
        commit.author_email = 'bruce@lee.com'
        commit.author = None
        hunk_key.parent.return_value.get.return_value = commit

        first_query.filter.return_value = second_query
        second_query.filter.return_value = third_query
        third_query.order.return_value = fourth_query
        fourth_query.get.return_value = commit_hunk
        mock_query.return_value = first_query

        repo = Mock()
        repo.key = Mock()
        filename = 'foo'
        line_number = 5

        name, email, user = blame.blame(repo, filename, line_number)

        self.assertEqual(commit.author_name, name)
        self.assertEqual(commit.author_email, email)
        self.assertIsNone(user)
        mock_query.assert_called_once_with(ancestor=repo.key)
        first_query.filter.assert_called_once_with(
            CommitHunk.filename == filename)
        second_query.filter.assert_called_once_with(
            CommitHunk.lines == line_number)
        third_query.order.assert_called_once_with(-CommitHunk.timestamp)
        fourth_query.get.assert_called_once_with()

