from google.appengine.ext import ndb


class User(ndb.Model):

    username = ndb.StringProperty(required=False)
    github_access_token = ndb.StringProperty()

