import json
import sys
import time
import unittest

from mock import Mock
from mock import patch

import kaput


class TestInit(unittest.TestCase):

    def tearDown(self):
        # Reset the excepthook to original state.
        sys.excepthook = sys.__excepthook__
        kaput._DEBUG = False
        kaput._API_KEY = None

    def test_no_api_key(self):
        """Ensure that an exception is raised when None is passed in as an API
        key.
        """

        self.assertRaises(Exception, kaput.init, None, '123')

    def test_no_project_id(self):
        """Ensure that an exception is raised when None is passed in as a
        project id.
        """

        self.assertRaises(Exception, kaput.init, 'abc', None)

    def test_set_properties(self):
        """Ensure _DEBUG, _API_KEY, and _PROJECT_ID are correctly set and the
        excepthook is patched.
        """

        api_key = 'abc'
        project_id = '123'

        kaput.init(api_key, project_id, debug=True)

        self.assertEqual(api_key, kaput._API_KEY)
        self.assertEqual(project_id, kaput._PROJECT_ID)
        self.assertTrue(kaput._DEBUG)
        self.assertEqual(kaput._handle_exception, sys.excepthook)

    def test_set_api_key(self):
        """Ensure _DEBUG, _API_KEY, and _PROJECT_ID are correctly set and the
        excepthook is patched when the debug kwarg is not specified.
        """

        api_key = 'abc'
        project_id = '123'

        kaput.init(api_key, project_id)

        self.assertEqual(api_key, kaput._API_KEY)
        self.assertEqual(project_id, kaput._PROJECT_ID)
        self.assertFalse(kaput._DEBUG)
        self.assertEqual(kaput._handle_exception, sys.excepthook)


@patch('kaput.sys.__excepthook__')
@patch('kaput.time')
@patch('kaput.traceback')
@patch('kaput._HTTP')
class TestHandleException(unittest.TestCase):

    def setUp(self):
        self.api_key = 'abc'
        self.project_id = '123'
        kaput._API_KEY = self.api_key
        kaput._PROJECT_ID = self.project_id

    def tearDown(self):
        kaput._API_KEY = None
        kaput._PROJECT_ID = None

    def test_handle_exception(self, mock_http, mock_tb, mock_time,
                              mock_excepthook):
        """Ensure _handle_exception makes a request to the correct endpoint
        with the correct payload.
        """

        mock_traceback = Mock()
        exc_type = TypeError
        message = 'oh snap'
        exception = exc_type(message)

        mock_tb.extract_tb.return_value = [
            ('foo.py', 42, 'foo', 'return bar()'),
            ('bar.py', 101, 'bar', 'return baz(x)'),
            ('baz.py', 34, 'baz', 'return x + 1')
        ]
        mock_tb.format_tb.return_value = 'this is a traceback'
        now = time.time()
        mock_time.time.return_value = now

        kaput._handle_exception(exc_type, exception, mock_traceback)

        mock_tb.extract_tb.assert_called_once_with(mock_traceback)
        mock_tb.format_tb.assert_called_once_with(mock_traceback)
        mock_http.request.assert_called_once_with(
            'https://kaput-dev.appspot.com/api/v1/exception',
            method='POST',
            headers={'kaput-api-key': self.api_key,
                     'Content-Type': 'application/json'},
            body=json.dumps({
                'project_id': self.project_id,
                'timestamp': now,
                'exception': exc_type.__name__,
                'message': message,
                'frames': mock_tb.extract_tb.return_value,
                'stacktrace': mock_tb.format_tb.return_value
            })
        )
        mock_excepthook.assert_called_once_with(
            exc_type, exception, mock_traceback)

