import time
import unittest
from google.appengine.ext import testbed

from hashing import make_pw_hash
from repositories import (BlogRepository,
                          UserRepository)
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
        assert UserRepository.username_not_taken(username)
        user.put()
        assert not UserRepository.username_not_taken(username)
        user_id = UserRepository.user_id_from_username_password(username,
                                                                password)
        assert user_id == user.key().id()

    def test_email_from_username(self):
        username = "test_user"
        password = "test"
        email = "test@test.com"
        pw_hash = make_pw_hash(username, password)
        user = User(username=username, password_hash_salt=pw_hash, email=email)
        user.put()
        assert UserRepository.email_from_username(username) == email


class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def teardown(self):
        self.testbed.deactivate()

    def test_get_username(self):
        content = "What a great entry"
        subject = "Test Subject"
        blog = Blog(subject=subject, content=content)
        blog.put()
        assert set(Blog.get_json(blog).keys()) == {'subject', 'content',
                                                   'created'}

    def test_get_blog_by_id(self):
        blog = Blog(subject="Subject1", content="Content1")
        n = blog.put()
        blog_id = n.id()
        blog1, cache_age1 = BlogRepository.get_blog_by_id(blog_id)
        assert cache_age1 < .01
        time.sleep(.1)
        blog2, cache_age2 = BlogRepository.get_blog_by_id(blog_id)
        assert cache_age2 > .1

    def test_get_blog_posts(self):
        blog1 = Blog(subject="Subject1", content="Content1")
        blog1.put()
        blog_posts, cache_age = BlogRepository.get_blog_posts()
        assert cache_age < .01
        assert "Subject1" == blog_posts[0].subject
        time.sleep(.1)
        results2, cache_age2 = BlogRepository.get_blog_posts()
        assert cache_age2 > .1

    def test_put(self):
        blog_posts, cache_age = BlogRepository.get_blog_posts()
        assert len(blog_posts) == 0
        blog = Blog(subject="Subject", content="Content")
        time.sleep(.1)
        BlogRepository.put(blog)
        blog_posts2, cache_age2 = BlogRepository.get_blog_posts()
        assert len(blog_posts2) == 1
        assert cache_age2 < .01


if __name__ == '__main__':
    unittest.main()
