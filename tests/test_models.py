from datetime import (datetime,
                      timedelta)
import unittest
from google.appengine.ext import testbed

from models import (Blog,
                    ResetToken)


class ResetTokenTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def teardown(self):
        self.testbed.deactivate()

    def test_is_valid(self):
        time_created = datetime.now() - timedelta(hours=6)
        token = ResetToken(username="user",
                           name_time_hash="test",
                           time_created=time_created,
                           active=True)
        token.put()
        assert token.is_valid()
        token.active = False
        token.put()
        assert not token.is_valid()
        token.active = True
        token.put()
        assert token.is_valid()
        token.time_created = datetime.now() - timedelta(hours=13)
        token.put()
        assert not token.is_valid()


class UserTestCase(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def teardown(self):
        self.testbed.deactivate()


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


if __name__ == '__main__':
    unittest.main()
