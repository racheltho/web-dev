import webapp2
from main import app


class TestSignUp():

    def test_get(self):
        request = webapp2.Request.blank('/blog/signup')
        response = request.get_response(app)
        assert response.status_code == 200
        assert 'Username' in response.body
        assert 'New users:' in response.body

    def test_post_errors(self):
        params = {'username': 'thisisatest',
                  'password': '123',
                  'verify': '123',
                  'email': 'r@t.com',
                  }
        request = webapp2.Request.blank('/blog/signup', POST=params)
        response = request.get_response(app)
        assert response.status_code == 500
        # assert response.location == 'http://localhost/blog/signup'
        # assert response.status_code == 400
        # assert 'Welcome, Rachel!' in response.body

