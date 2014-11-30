import webapp2
import cgi
import jinja2
import os.path
import datetime
from google.appengine.ext import db

import validation


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


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


class AsciiPage(Handler):

    def render_ascii(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC")
        self.render("ascii.html", title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_ascii()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')

        if title and art:
            new_art = Art(title=title, art=art)
            new_art.put()
            self.redirect("/")
        else:
            error = "we need both a title and artwork!"
            self.render_ascii(title=title, art=art, error=error)


class SignupPage(Handler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.render("signup.html")

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
            self.render("signup.html", **kwargs)
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


app = webapp2.WSGIApplication([('/', AsciiPage),
                              ('/signup', SignupPage),
                              ('/welcome', WelcomePage),
                              ('/fizzbuzz', FizzBuzzPage)],
                              debug=True
                              )
