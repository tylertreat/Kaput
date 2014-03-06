from datetime import datetime
import logging

from google.appengine.api import mail
from google.appengine.ext import ndb

from furious import context
from furious.async import defaults
from furious.errors import Abort

from kaput.blame import blame
from kaput.repository import Repository


NOTIFICATION_QUEUE = 'notification-processor'


class Issue(ndb.Model):

    repo = ndb.KeyProperty(kind=Repository)
    timestamp = ndb.DateTimeProperty()
    exception = ndb.StringProperty()
    message = ndb.StringProperty(indexed=False)
    frames = ndb.JsonProperty()
    stacktrace = ndb.TextProperty()
    contacts = ndb.StringProperty(repeated=True)


def process_exception(data):
    """Process the exception data."""

    project_id = data['project_id']

    repo = Repository.get_by_id(project_id)

    if not repo or not repo.enabled:
        raise Abort('Repo %s is not enabled' % project_id)

    unix_timestamp = data['timestamp']
    timestamp = datetime.fromtimestamp(unix_timestamp)
    exception = data['exception']
    message = data['message']
    frames = data['frames']
    stacktrace = data['stacktrace']

    issue = Issue(repo=repo.key, timestamp=timestamp, exception=exception,
                  message=message, frames=frames, stacktrace=stacktrace,
                  contacts=[])

    issue.put()

    logging.debug('Saved new issue for repo %s' % project_id)

    with context.new() as ctx:
        for filename, line_no, func, text in frames:
            ctx.add(target=notify,
                    args=(project_id, issue.key.id(), unix_timestamp, filename,
                          line_no, func, text, stacktrace))

    logging.debug('Inserted %s notify tasks' % ctx.insert_success)


@defaults(queue=NOTIFICATION_QUEUE)
def notify(project_id, issue_id, timestamp, filename, line_no, func, text,
           stacktrace):
    """Notify the person responsible."""

    repo = Repository.get_by_id(project_id)

    if not repo or not repo.enabled:
        raise Abort('Repo %s is not enabled' % project_id)

    author_name, author_email, author = blame(repo, filename, line_no)

    if not author_email:
        raise Abort('Could not find contact for issue %s' % issue_id)

    timestamp = datetime.fromtimestamp(timestamp)

    sender = 'mail@kaput-dev.appspotmail.com'
    subject = 'Error Reported in %s [%s]' % (repo.name, timestamp)
    body = ('Hi %s,\n\nAn error has occurred in %s. Our records indicate you '
            'were the last person to touch the impacted code: \n\n%s:%s %s '
            '%s\n\n%s') % (repo.name, filename, line_no, func, text,
                           stacktrace)

    mail.send_mail(sender, author_email, subject, body)

    @ndb.transactional
    def update_issue():
        issue = Issue.get_by_id(issue_id)
        issue.contacts.append(author_email)
        issue.put()

    update_issue()

