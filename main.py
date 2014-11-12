import webapp2
import cgi

import validation

form = """
<title>Awesome Signup</title>
<form method="post" action="/">
    <label>Username: <input name="username" value={username}></label>
    <div style="color: red">{username_error}</div><br>
    <label>Password:
    <input type="password" name="password" value={password}>
    </label>
    <div style="color: red">{password_error}</div><br>
    <label>Verify password:
    <input type="password" name="verify" value={verify}>
    </label>
    <div style="color: red">{verify_error}</div><br>
    <label>Email: <input name="email" value={email}></label>
    <div style="color: red">{email_error}</div><br>
    <br><input type="submit">
</form>
"""


class MainPage(webapp2.RequestHandler):

    def write_form(self,
                   username="",
                   email="",
                   username_error="",
                   password_error="",
                   verify_error="",
                   email_error=""
                   ):
        self.response.out.write(form.format(username=username,
                                            email=email,
                                            password="",
                                            verify="",
                                            username_error=username_error,
                                            password_error=password_error,
                                            verify_error=verify_error,
                                            email_error=email_error,
                                            ))

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.write_form()

    def post(self):

        kwargs = {}

        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        valid_username = validation.valid_username(username)
        valid_password = validation.valid_password(password)
        valid_verify = (verify == password)
        valid_email = validation.valid_email(email)

        username = cgi.escape(username)
        email = cgi.escape(email)

        kwargs['username'] = username
        kwargs['email'] = email

        if not valid_username:
            kwargs['username_error'] = "That's not a valid username"
        if not valid_password:
            kwargs['password_error'] = "That wasn't a valid password"
        if not valid_verify:
            kwargs['verify_error'] = "Your passwords didn't match"
        if not valid_email:
            kwargs['email_error'] = "That's not a valid email"

        error_dict = {'username_error',
                      'password_error',
                      'verify_error',
                      'email_error'
                      }

        # check if any error messages are in kwargs
        if error_dict & set(kwargs.keys()) != set():
            self.write_form(**kwargs)
        else:
            self.response.out.write("You were successful, {}!".format(username))


app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True
                              )
