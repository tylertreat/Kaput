import unittest

from mock import Mock
from mock import patch

from kaput.services import gh


class TestGetWebhook(unittest.TestCase):

    def test_hook_exists(self):
        """Ensure that if the hook exists, it's returned."""

        url = 'url'
        repo = Mock()
        mock_owner_key = Mock()
        mock_owner = Mock()
        mock_repo = Mock()
        hook1 = Mock()
        hook1.config = {'url': url}
        hook2 = Mock()
        hook2.config = {'url': 'foo'}
        mock_repo.get_hooks.return_value = [hook1, hook2]
        mock_owner.get_github_repo.return_value = mock_repo
        mock_owner_key.get.return_value = mock_owner
        repo.owner = mock_owner_key

        actual = gh.get_webhook(repo, url)

        self.assertEqual(hook1, actual)
        mock_repo.get_hooks.assert_called_once_with()

    def test_hook_does_not_exist(self):
        """Ensure that if the hook doesn't exist, None is returned."""

        url = 'url'
        repo = Mock()
        mock_owner_key = Mock()
        mock_owner = Mock()
        mock_repo = Mock()
        hook1 = Mock()
        hook1.config = {'url': 'bar'}
        hook2 = Mock()
        hook2.config = {'url': 'foo'}
        mock_repo.get_hooks.return_value = [hook1, hook2]
        mock_owner.get_github_repo.return_value = mock_repo
        mock_owner_key.get.return_value = mock_owner
        repo.owner = mock_owner_key

        actual = gh.get_webhook(repo, url)

        self.assertIsNone(actual)
        mock_repo.get_hooks.assert_called_once_with()


@patch('kaput.services.gh.get_webhook')
class TestCreateWebhook(unittest.TestCase):

    def setUp(self):
        self.repo = Mock()
        mock_owner_key = Mock()
        mock_owner = Mock()
        self.mock_repo = Mock()
        mock_owner.get_github_repo.return_value = self.mock_repo
        mock_owner_key.get.return_value = mock_owner
        self.repo.owner = mock_owner_key

    def test_has_hook(self, mock_get_hook):
        """Ensure that True is returned if the hook already exists."""

        url = 'url'

        self.assertTrue(gh.create_webhook(self.repo, url))
        mock_get_hook.assert_called_once_with(self.repo, url)

    def test_create(self, mock_get_hook):
        """Ensure that True is returned and the hook is created if it doesn't
        exist.
        """

        url = 'url'
        mock_get_hook.return_value = None

        self.assertTrue(gh.create_webhook(self.repo, url))
        mock_get_hook.assert_called_once_with(self.repo, url)
        self.mock_repo.create_hook.assert_called_once_with(
            'web', {'url': url, 'content_type': 'json'}, events=['push'],
            active=True
        )


@patch('kaput.services.gh.get_webhook')
class TestDeleteWebHook(unittest.TestCase):

    def test_has_hook(self, mock_get_hook):
        """Ensure that if the hook exists, it's deleted and True is returned.
        """

        repo = Mock()
        url = 'url'

        self.assertTrue(gh.delete_webhook(repo, url))
        mock_get_hook.assert_called_once_with(repo, url)
        mock_get_hook.return_value.delete.assert_called_once_with()

    def test_no_hook(self, mock_get_hook):
        """Ensure that if the hook doesn't exist, nothing is done and False is
        returned.
        """

        repo = Mock()
        url = 'url'
        mock_get_hook.return_value = None

        self.assertFalse(gh.delete_webhook(repo, url))
        mock_get_hook.assert_called_once_with(repo, url)

