from google.appengine.ext import testbed
import unittest
import webapp2
import webtest
import Cookie

import hashing
from main import (BlogMainHandler,
                  NewPostHandler,
                  SignupHandler,
                  PermalinkHandler)
from models import (User,
                    Blog)


#class BlogMainTest(unittest.TestCase):
#
#    def set_cookie(self, key, value):
#        self.cookies[key] = value
#
#    def setUp(self):
#        app = webapp2.WSGIApplication([('/blog', BlogMainHandler)])
#        self.testapp = webtest.TestApp(app)
#        self.testbed = testbed.Testbed()
#        self.testbed.activate()
#        self.testbed.init_datastore_v3_stub()
#        self.testbed.init_memcache_stub()
#        self.cookies = Cookie.BaseCookie()
#
#    def tearDown(self):
#        self.testbed.deactivate()
#
#    def testBlogMain(self):
#        new_blog = Blog(subject="test_subject", content="test_content")
#        new_blog.put()
#        new_user = User(username="test_user", password_hash_salt="pwhs")
#        n = new_user.put()
#        user_id = n.id()
#        hashed_cookie = hashing.make_secure_val(user_id)
#        self.set_cookie('user_id', hashed_cookie)
#        response = self.testapp.get('/blog')
#        assert response.status_code == 200
#        assert "test_subject" in response.body


class SignUpTest(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/blog/signup', SignupHandler)])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def test_post(self):
        params = {'username': 'thisisatest',
                  'password': '123',
                  'verify': '123',
                  'email': 'r@t.com',
                  }
        response = self.testapp.post('/blog/signup', params)
        assert response.status_code == 302
        assert response.location == 'http://localhost/blog/welcome'
