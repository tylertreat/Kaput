import unittest

from mock import call
from mock import Mock
from mock import patch

from kaput.auth import user


@patch('kaput.auth.user.context')
@patch('kaput.auth.user.User.query')
class TestPublicSyncUsers(unittest.TestCase):

    def test_chain(self, mock_query, mock_context):
        """Ensure that sync_users inserts a task for syncing a batch of users
        and a task for itself if there are more users left to sync.
        """

        context = Mock()
        mock_context.new.return_value.__enter__.return_value = context
        query = Mock()
        key1 = Mock()
        key2 = Mock()
        cursor = Mock()
        query.fetch_page.return_value = ([key1, key2], cursor, True)
        mock_query.return_value = query

        user.sync_users()

        mock_query.assert_called_once_with()
        query.fetch_page.assert_called_once_with(100, start_cursor=None,
                                                 keys_only=True)
        mock_context.new.assert_called_once_with()
        expected = [
            call(target=user._sync_users, args=([key1.id.return_value,
                                                 key2.id.return_value],)),
            call(target=user.sync_users, kwargs={'cursor':
                                                 cursor.urlsafe.return_value})
        ]
        self.assertEqual(expected, context.add.call_args_list)

    @patch('kaput.auth.user.Cursor')
    def test_no_chain(self, mock_cursor, mock_query, mock_context):
        """Ensure that sync_users inserts a task for syncing a batch of users
        and no task for itself if there are no more users left to sync.
        """

        context = Mock()
        mock_context.new.return_value.__enter__.return_value = context
        query = Mock()
        key1 = Mock()
        key2 = Mock()
        query.fetch_page.return_value = ([key1, key2], None, False)
        mock_query.return_value = query
        cursor = 'cursor'

        user.sync_users(cursor=cursor)

        mock_query.assert_called_once_with()
        mock_cursor.assert_called_once_with(urlsafe=cursor)
        query.fetch_page.assert_called_once_with(
            100, start_cursor=mock_cursor.return_value, keys_only=True)
        mock_context.new.assert_called_once_with()
        context.add.assert_called_once_with(target=user._sync_users,
                                            args=([key1.id.return_value,
                                                   key2.id.return_value],))


@patch('kaput.auth.user.sync_github_user')
@patch('kaput.auth.user.ndb')
class TestSyncUsers(unittest.TestCase):

    def test_sync(self, mock_ndb, mock_sync):
        """Ensure that users are retrieved and synced."""

        key1 = Mock()
        key2 = Mock()
        mock_ndb.Key.side_effect = [key1, key2]
        mock_user = Mock()
        mock_ndb.get_multi.return_value = [mock_user, None]
        ids = ['user1', 'user2']

        user._sync_users(ids)

        expected = [call(user.User, user_id) for user_id in ids]
        self.assertEqual(expected, mock_ndb.Key.call_args_list)
        mock_ndb.get_multi.assert_called_once_with([key1, key2])
        mock_sync.assert_called_once_with(mock_user)

