from datetime import datetime
from google.appengine.api import memcache
from google.appengine.ext import db

from models import Blog
import hashing


def age_set(key, value):
    save_time = datetime.now()
    memcache.set(key, (save_time, value))


def age_get(key):
    results = memcache.get(key)
    if results:
        save_time, value = results
        age = (datetime.now() - save_time).total_seconds()
    else:
        value, age = None, 0
    return value, age


class UserRepository():
    @classmethod
    def user_id_from_username_password(cls, username, password):
        user = db.GqlQuery("SELECT * FROM User "
                           "WHERE username = '{}'".format(username)).get()
        if user:
            h = user.password_hash_salt
            if hashing.valid_pw(username, password, h):
                return user.key().id()

    @classmethod
    def username_not_taken(cls, username):
        query = db.GqlQuery("SELECT * FROM User "
                            "WHERE username = '{}'".format(username))
        if not query.get():
            return True


class BlogRepository():

    @classmethod
    def get_blog_by_id(cls, blog_id):
        value, age = age_get(str(blog_id))
        if value is None:
            value = Blog.get_by_id(int(blog_id))
            age_set(str(blog_id), value)
        return value, age

    @classmethod
    def get_blog_posts(cls):
        value, age = age_get('blog_posts')
        if value is None:
            value = db.GqlQuery("SELECT * FROM Blog "
                                "ORDER BY created DESC "
                                "LIMIT 10")
            age_set('blog_posts', value)
        return list(value), age

    @classmethod
    def put(cls, blog):
        memcache.delete('blog_posts')
        return blog.put()
