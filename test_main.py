import webapp2
import main


class TestHandlers():

    def test_get(self):
        request = webapp2.Request.blank('/')
        response = request.get_response(main.app)
        assert response.status_code == 200
        assert 'Username' in response.body

    def test_post_successful(self):
        params = {'username': 'rachel',
                  'password': '123',
                  'verify': '123',
                  'email': 'r@t.com',
                  }
        request = webapp2.Request.blank('/', POST=params)
        response = request.get_response(main.app)
        assert response.body == 'You were successful, rachel!'
        assert response.status_code == 200

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
