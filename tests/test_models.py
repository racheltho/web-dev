import unittest
from google.appengine.ext import testbed

from models import Blog


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
