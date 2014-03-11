from datetime import datetime
import time
import unittest

from furious.errors import Abort

from gaeutils.test import DatastoreTestCase

from mock import call
from mock import Mock
from mock import patch

from kaput import report


@patch('kaput.report.Repository.get_by_id')
class TestProcessException(unittest.TestCase):

    def test_no_repo(self, mock_get_by_id):
        """Ensure that if the repo doesn't exist, Abort is raised."""

        mock_get_by_id.return_value = None
        project_id = 'abc'
        data = {'project_id': project_id}

        self.assertRaises(Abort, report.process_exception, data)
        mock_get_by_id.assert_called_once_with(project_id)

    @patch('kaput.report.context')
    @patch('kaput.report.Issue')
    def test_fan_out(self, mock_issue_init, mock_context, mock_get_by_id):
        """Ensure that an Issue is created for the exception and tasks are
        inserted for each stack frame.
        """

        mock_repo = Mock()
        mock_repo.key = Mock()
        mock_get_by_id.return_value = mock_repo
        context = Mock()
        context.insert_success = 2
        mock_context.new.return_value.__enter__.return_value = context
        mock_issue = Mock()
        issue_key = Mock()
        issue_key.id.return_value = '123'
        mock_issue.key = issue_key
        mock_issue_init.return_value = mock_issue

        project_id = 'abc'
        timestamp = time.time()
        exception = 'ValueError'
        message = 'oh snap!'
        frame1 = ('foo.py', 24, 'foobar', 'return bar()')
        frame2 = ('bar.py', 120, 'baz', 'raise ValueError')
        frames = [frame1, frame2]
        stacktrace = 'stacktrace'

        data = {
            'project_id': project_id,
            'timestamp': timestamp,
            'exception': exception,
            'message': message,
            'frames': frames,
            'stacktrace': stacktrace
        }

        report.process_exception(data)

        mock_get_by_id.assert_called_once_with(project_id)

        mock_issue_init.assert_called_once_with(
            repo=mock_repo.key, timestamp=datetime.fromtimestamp(timestamp),
            exception=exception, message=message, frames=frames,
            stacktrace=stacktrace, contacts=[])
        mock_issue.put.assert_called_once_with()

        expected = [
            call(target=report.notify,
                 args=(project_id, issue_key.id.return_value, timestamp,
                       frame1[0], frame1[1], frame1[2], frame1[3],
                       stacktrace)),
            call(target=report.notify,
                 args=(project_id, issue_key.id.return_value, timestamp,
                       frame2[0], frame2[1], frame2[2], frame2[3], stacktrace))
        ]
        self.assertEqual(expected, context.add.call_args_list)


@patch('kaput.report.Repository.get_by_id')
class TestNotify(DatastoreTestCase):

    def setUp(self):
        self.project_id = 'abc'
        self.issue_id = '123'
        self.timestamp = time.time()
        self.filename = 'foo.py'
        self.line_no = 42
        self.func = 'foobar'
        self.text = 'raise ValueError()'
        self.stacktrace = 'stacktrace'

        super(TestNotify, self).setUp()

    def test_no_repo(self, mock_get_by_id):
        """Ensure that if the repo doesn't exist, Abort is raised."""

        mock_get_by_id.return_value = None

        self.assertRaises(Abort, report.notify, self.project_id, self.issue_id,
                          self.timestamp, self.filename, self.line_no,
                          self.func, self.text, self.stacktrace)

        mock_get_by_id.assert_called_once_with(self.project_id)

    @patch('kaput.report.blame')
    def test_no_contact(self, mock_blame, mock_get_by_id):
        """Ensure that if no contact is found, Abort is raised."""

        mock_blame.return_value = None, None, None

        self.assertRaises(Abort, report.notify, self.project_id, self.issue_id,
                          self.timestamp, self.filename, self.line_no,
                          self.func, self.text, self.stacktrace)

        mock_get_by_id.assert_called_once_with(self.project_id)
        mock_blame.assert_called_once_with(
            mock_get_by_id.return_value, self.filename, self.line_no)

    @patch('kaput.report.Issue.get_by_id')
    @patch('kaput.report.mail.send_mail')
    @patch('kaput.report.blame')
    def test_email_contact(self, mock_blame, mock_mail, mock_get_issue,
                           mock_get_repo):
        """Ensure that if a contact is found, an email alert is sent."""

        author_name = 'Tyler'
        author_email = 'ttreat31@gmail.com'

        mock_blame.return_value = author_name, author_email, None
        mock_repo = Mock()
        mock_repo.name = 'repo'
        mock_get_repo.return_value = mock_repo
        mock_issue = Mock()
        mock_issue.contacts = []
        mock_get_issue.return_value = mock_issue

        report.notify(self.project_id, self.issue_id, self.timestamp,
                      self.filename, self.line_no, self.func, self.text,
                      self.stacktrace)

        mock_get_repo.assert_called_once_with(self.project_id)
        mock_blame.assert_called_once_with(
            mock_get_repo.return_value, self.filename, self.line_no)

        mock_mail.assert_called_once_with(
            'mail@kaput-dev.appspotmail.com', author_email,
            'Error Reported in %s [%s]' %
            (mock_repo.name, datetime.fromtimestamp(self.timestamp)),
            ('Hi %s,\n\nAn error has occurred in %s. It looks like you may '
             'have been the last person to touch the impacted code: '
             '\n\n%s:%s %s %s\n\n%s') % (author_name, mock_repo.name,
                                         self.filename, self.line_no,
                                         self.func, self.text, self.stacktrace)
        )

        mock_get_issue.assert_called_once_with(self.issue_id)
        mock_issue.put.assert_called_once_with()
        self.assertEqual([author_email], mock_issue.contacts)

