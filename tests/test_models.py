import unittest
from google.appengine.ext import testbed

from hashing import make_pw_hash
from models import (Blog,
                    User)


class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def teardown(self):
        self.testbed.deactivate()

    def test_get_username(self):
        username = "test_user"
        password = "password"
        password_hash_salt = make_pw_hash(username, password)
        user = User(username=username, password_hash_salt=password_hash_salt)
        assert User.username_not_taken(username)
        user.put()
        assert not User.username_not_taken(username)
        user_id = User.user_id_from_username_password(username, password)
        assert user_id == user.key().id()


class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def teardown(self):
        self.testbed.deactivate()

    def test_get_username(self):
        content = "What a great entry"
        subject = "Test Subject"
        blog = Blog(subject=subject, content=content)
        blog.put()
        assert set(Blog.get_json(blog).keys()) == {'subject', 'content', 'created'} 

if __name__ == '__main__':
    unittest.main()
