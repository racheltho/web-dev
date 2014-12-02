import webapp2
import jinja2
import os.path
from google.appengine.ext import db

import validation
import hashing


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class Blog(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class User(db.Model):
    username = db.StringProperty(required=True)
    password_hash_salt = db.StringProperty(required=True)
    email = db.StringProperty(required=True)


def username_not_taken(username):
    query = db.GqlQuery("SELECT * FROM User "
                        "WHERE username = '{}'".format(username))
    if not query.get():
        return True


class Handler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))


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

        new_username = username_not_taken(username)
        valid_username = validation.valid_username(username)
        valid_password = validation.valid_password(password)
        valid_verify = (verify == password)
        valid_email = validation.valid_email(email)

        kwargs['username'] = username
        kwargs['email'] = email

        if not new_username:
            kwargs['username_exists'] = "That user already exists"
        if not valid_username:
            kwargs['username_error'] = "That's not a valid username"
        if not valid_password:
            kwargs['password_error'] = "That wasn't a valid password"
        if not valid_verify:
            kwargs['verify_error'] = "Your passwords didn't match"
        if not valid_email:
            kwargs['email_error'] = "That's not a valid email"

        error_dict = {'username_exists',
                      'username_error',
                      'password_error',
                      'verify_error',
                      'email_error'
                      }

        # check if any error messages are in kwargs
        if error_dict & set(kwargs.keys()) != set():
            self.render("signup.html", **kwargs)
        else:
            # salt and hash password
            password_hash_salt = hashing.make_pw_hash(username, password)

            # create new user
            new_user = User(username=username,
                            password_hash_salt=password_hash_salt,
                            email=email
                            )
            n = new_user.put()
            user_id = n.id()

            # create cookie useing hashed id
            hashed_cookie = hashing.make_secure_val(user_id)
            self.response.headers.add_header('Set-Cookie',
                                             'user_id={}; '
                                             'Path=/'.format(hashed_cookie))
            self.redirect("/blog/welcome")


class WelcomePage(Handler):

    def get(self):
        hashed_user_id = self.request.cookies.get('user_id')
        kwargs = {}
        if hashed_user_id:
            user_id = hashing.check_secure_val(hashed_user_id)
            try:
                user = User.get_by_id(int(user_id))
                self.render("welcome.html", username=user.username)
            except TypeError:
                self.redirect("/blog/signup")
        else:
            self.redirect("/blog/signup")


class BlogMainPage(Handler):

    def render_blog_main_page(self):
        blog_posts = db.GqlQuery("SELECT * FROM Blog "
                                 "ORDER BY created DESC")
        self.render("blog.html", blog_posts=blog_posts)

    def get(self):
        self.render_blog_main_page()


class NewPostPage(Handler):

    def render_new_post(self, subject="", content="", error=""):
        self.render("newpost.html",
                    subject=subject,
                    content=content,
                    error=error
                    )

    def get(self):
        self.render_new_post()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            new_blog_post = Blog(subject=subject, content=content)
            new_blog_post.put()
            self.redirect("/blog/"+str(new_blog_post.key().id()))
        else:
            error = "we need both a subject and content!"
            self.render_new_post(subject=subject, content=content, error=error)


class PermalinkPage(Handler):

    def get(self, blog_id):
        blog = Blog.get_by_id(int(blog_id))
        self.render("permalink.html", blog=blog)


class MainPage(Handler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = self.request.cookies.get('visits', 0)
        try:
            visits = int(visits) + 1
        except ValueError:
            visits = 0
        self.response.headers.add_header('Set-Cookie',
                                         'visits={}'.format(visits))
        if visits == 10:
            self.write("Thanks for visiting 10 times!")
        else:
            self.write("You've been here {} times!".format(visits))


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
            self.redirect("/ascii")
        else:
            error = "we need both a title and artwork!"
            self.render_ascii(title=title, art=art, error=error)


app = webapp2.WSGIApplication([('/blog', BlogMainPage),
                              ('/blog/newpost', NewPostPage),
                              ('/blog/(\d+)', PermalinkPage),
                              ('/', MainPage),
                              ('/ascii', AsciiPage),
                              ('/blog/signup', SignupPage),
                              ('/blog/welcome', WelcomePage)],
                              debug=True
                              )
