from google.appengine.ext import ndb

from kaput.user import User


class Repository(ndb.Model):

    name = ndb.StringProperty()
    owner = ndb.KeyProperty(kind=User)
    enabled = ndb.BooleanProperty(default=False)


class Commit(ndb.Model):

    repo = ndb.KeyProperty(kind=Repository)
    sha = ndb.StringProperty(indexed=False)
    author_name = ndb.StringProperty(indexed=False)
    author_email = ndb.StringProperty(indexed=False)
    author_date = ndb.DateTimeProperty(indexed=False)
    committer_name = ndb.StringProperty(indexed=False)
    committer_email = ndb.StringProperty(indexed=False)
    committer_date = ndb.DateTimeProperty(indexed=False)
    author = ndb.JsonProperty(indexed=False, required=False)
    committer = ndb.JsonProperty(indexed=False, required=False)
    message = ndb.TextProperty(indexed=False, required=False)


class CommitChunk(ndb.Model):

    commit = ndb.KeyProperty(kind=Commit)
    filename = ndb.StringProperty()
    start_line = ndb.IntegerProperty()
    line_count = ndb.IntegerProperty(default=0)

