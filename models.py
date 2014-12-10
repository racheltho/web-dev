from google.appengine.ext import db

import hashing


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    coords = db.GeoPtProperty()


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


class User(db.Model):
    username = db.StringProperty(required=True)
    password_hash_salt = db.StringProperty(required=True)
    email = db.StringProperty()
    coords = db.GeoPtProperty()

    @staticmethod
    def user_id_from_username_password(username, password):
        user = db.GqlQuery("SELECT * FROM User "
                           "WHERE username = '{}'".format(username)).get()
        if user:
            h = user.password_hash_salt
            if hashing.valid_pw(username, password, h):
                return user.key().id()

    @staticmethod
    def username_not_taken(username):
        query = db.GqlQuery("SELECT * FROM User "
                            "WHERE username = '{}'".format(username))
        if not query.get():
            return True
