from google.appengine.ext import db
from datetime import (datetime,
                      timedelta)


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def get_json(self):
        blog_json = {"content": self.content,
                     "subject": self.subject,
                     "created": self.created.strftime("%c")}
        return blog_json


class ResetToken(db.Model):
    username = db.StringProperty(required=True)
    time_created = db.DateTimeProperty(required=True)
    name_time_hash = db.StringProperty(required=True)
    active = db.BooleanProperty(required=True, default=True)

    def is_valid(self):
        time_limit = timedelta(hours=12)
        now = datetime.now()
        if self.active and (now - self.time_created <= time_limit):
            return True

    def set_used(self):
        self.active = False


class User(db.Model):
    username = db.StringProperty(required=True)
    password_hash_salt = db.StringProperty(required=True)
    email = db.StringProperty()
    coords = db.GeoPtProperty()
