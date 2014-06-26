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

        actual = gh.get_webhooks(repo, [url])

        self.assertEqual([hook1], actual)
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

        actual = gh.get_webhooks(repo, [url])

        self.assertEqual([], actual)
        mock_repo.get_hooks.assert_called_once_with()


class TestCreateWebhook(unittest.TestCase):

    def setUp(self):
        self.repo = Mock()
        mock_owner_key = Mock()
        mock_owner = Mock()
        self.mock_repo = Mock()
        mock_owner.get_github_repo.return_value = self.mock_repo
        mock_owner_key.get.return_value = mock_owner
        self.repo.owner = mock_owner_key

    def test_has_hook(self):
        """Ensure that True is returned if the hook already exists."""

        url = 'url'

        self.assertTrue(gh.create_webhook(self.repo, url))

    def test_create(self):
        """Ensure that True is returned and the hook is created if it doesn't
        exist.
        """
        from github.GithubException import GithubException

        url = 'url'
        self.mock_repo.create_hook.side_effect = GithubException(422, 'snap')

        self.assertTrue(gh.create_webhook(self.repo, url))
        self.mock_repo.create_hook.assert_called_once_with(
            'web', {'url': url, 'content_type': 'json'}, events=['push'],
            active=True
        )


@patch('kaput.services.gh.get_webhooks')
class TestDeleteWebHook(unittest.TestCase):

    def test_has_hook(self, mock_get_hooks):
        """Ensure that if the hook exists, it's deleted and True is returned.
        """

        repo = Mock()
        url = 'url'

        self.assertTrue(gh.delete_webhook(repo, url))
        mock_get_hooks.assert_called_once_with(repo, (url,))
        mock_get_hooks.return_value[0].delete.assert_called_once_with()

    def test_no_hook(self, mock_get_hooks):
        """Ensure that if the hook doesn't exist, nothing is done and False is
        returned.
        """

        repo = Mock()
        url = 'url'
        mock_get_hooks.return_value = None

        self.assertFalse(gh.delete_webhook(repo, url))
        mock_get_hooks.assert_called_once_with(repo, (url,))


@patch('kaput.services.gh.Github')
class TestGetCommits(unittest.TestCase):

    def test_get_commits(self, mock_github):
        """Ensure that the correct Github api call is made."""

        github = Mock()
        mock_github.return_value = github
        repo = Mock()
        repo.key.id.return_value = 'github_123'
        token = 'abc'
        repo.owner.get.return_value.github_token = token

        actual = gh.get_commits(repo)

        self.assertEqual(github.get_repo.return_value.get_commits.return_value,
                         actual)
        mock_github.assert_called_once_with(token)
        github.get_repo.assert_called_once_with(123)
        github.get_repo.return_value.get_commits.assert_called_once_with()

