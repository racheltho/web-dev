import webapp2
import main


class TestWelcomePage():

    def test_get(self):
        request = webapp2.Request.blank('/welcome?username=Rachel')
        response = request.get_response(main.app)
        assert response.status_code == 200
        assert response.body == 'Welcome, Rachel!'


class TestMainPage():

    def test_get(self):
        request = webapp2.Request.blank('/')
        response = request.get_response(main.app)
        assert response.status_code == 200
        assert 'Username' in response.body

    def test_successful_post_redirects(self):
        params = {'username': 'rachel',
                  'password': '123',
                  'verify': '123',
                  'email': 'r@t.com',
                  }
        request = webapp2.Request.blank('/', POST=params)
        response = request.get_response(main.app)
        # import pytest; pytest.set_trace()
        assert response.location == 'http://localhost/welcome?username=rachel'
        assert response.status_code == 302

    def test_post_invalid(self):
        params = {'username': 'r',
                  'password': '1',
                  'verify': '123',
                  'email': 'r.com',
                  }
        request = webapp2.Request.blank('/', POST=params)
        response = request.get_response(main.app)
        assert 'That\'s not a valid username' in response.body
        assert 'value=r.com' in response.body
        assert response.status_code == 200
        assert response.status_code == 200
