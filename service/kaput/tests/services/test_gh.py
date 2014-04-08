import json
import unittest

from mock import Mock
from mock import patch

from kaput.services import gh


@patch('kaput.services.gh.settings')
@patch('kaput.services.gh.redirect')
class TestAuthorize(unittest.TestCase):

    def test_redirect(self, mock_redirect, mock_settings):
        """Ensure that authorize makes a redirect to GitHub's OAuth endpoint
        with the correct scopes.
        """

        mock_redirect.return_value = 'redirect'
        mock_settings.GITHUB_CLIENT_ID = 'client_id'
        expected = 'https://github.com/login/oauth/authorize' \
            '?scope=repo,user:email&client_id=client_id'

        actual = gh.authorize()

        self.assertEqual(mock_redirect.return_value, actual)
        mock_redirect.assert_called_once_with(expected)


@patch('kaput.services.gh.settings')
@patch('kaput.services.gh.Http.request')
class TestExchangeForToken(unittest.TestCase):

    def test_non_200(self, mock_request, mock_settings):
        """Ensure that when a non-200 code is returned from the request, None
        is returned.
        """

        mock_response = Mock()
        mock_response.status = 500
        mock_request.return_value = mock_response, 'foo'
        mock_settings.GITHUB_CLIENT_ID = 'client_id'
        mock_settings.GITHUB_CLIENT_SECRET = 'secret'
        session_code = 'code'

        url = 'https://github.com/login/oauth/access_token'
        payload = json.dumps({
            'client_id': mock_settings.GITHUB_CLIENT_ID,
            'client_secret': mock_settings.GITHUB_CLIENT_SECRET,
            'code': session_code
        })

        actual = gh.exchange_for_token(session_code)

        self.assertIsNone(actual)
        mock_request.assert_called_once_with(
            url, method='POST', body=payload,
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        )

    def test_no_token(self, mock_request, mock_settings):
        """Ensure that when there is no access token in the response, None is
        returned.
        """

        mock_response = Mock()
        mock_response.status = 200
        mock_request.return_value = mock_response, '{"foo": "bar"}'
        mock_settings.GITHUB_CLIENT_ID = 'client_id'
        mock_settings.GITHUB_CLIENT_SECRET = 'secret'
        session_code = 'code'

        url = 'https://github.com/login/oauth/access_token'
        payload = json.dumps({
            'client_id': mock_settings.GITHUB_CLIENT_ID,
            'client_secret': mock_settings.GITHUB_CLIENT_SECRET,
            'code': session_code
        })

        actual = gh.exchange_for_token(session_code)

        self.assertIsNone(actual)
        mock_request.assert_called_once_with(
            url, method='POST', body=payload,
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        )

    def test_get_token(self, mock_request, mock_settings):
        """Ensure that when the response contains an access token, it's
        returned.
        """

        mock_response = Mock()
        mock_response.status = 200
        token = 'token'
        mock_request.return_value = (mock_response,
                                     '{"access_token": "%s"}' % token)
        mock_settings.GITHUB_CLIENT_ID = 'client_id'
        mock_settings.GITHUB_CLIENT_SECRET = 'secret'
        session_code = 'code'

        url = 'https://github.com/login/oauth/access_token'
        payload = json.dumps({
            'client_id': mock_settings.GITHUB_CLIENT_ID,
            'client_secret': mock_settings.GITHUB_CLIENT_SECRET,
            'code': session_code
        })

        actual = gh.exchange_for_token(session_code)

        self.assertEqual(token, actual)
        mock_request.assert_called_once_with(
            url, method='POST', body=payload,
            headers={'Accept': 'application/json',
                     'Content-Type': 'application/json'}
        )

