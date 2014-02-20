from google.appengine.ext import ndb

from flask.ext.login import UserMixin

from kaput.settings import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


class User(ndb.Model, UserMixin):

    username = ndb.StringProperty()
    email = ndb.StringProperty()
    github_access_token = ndb.StringProperty()

    def get_id(self):
        return self.key.id()

