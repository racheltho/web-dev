import webapp2
import cgi
import jinja2
import os.path

import validation


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))


class Handler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))


class WelcomePage(Handler):

    def get(self):
        kwargs = {'username': self.request.get('username')}
        self.render("welcome.html", **kwargs)


class MainPage(Handler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.render("input_form.html")

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
            self.render("input_form.html", **kwargs)
        else:
            self.redirect("/welcome?username={}".format(username))


class FizzBuzzPage(Handler):

    def get(self):
        n = self.request.get('n', 0)
        try:
            n = int(n)
        except ValueError:
            n = ""
        self.render('fizzbuzz.html', n=n)


app = webapp2.WSGIApplication([('/', MainPage),
                              ('/welcome', WelcomePage),
                              ('/fizzbuzz', FizzBuzzPage)],
                              debug=True
                              )
