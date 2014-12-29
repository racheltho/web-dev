import jinja2
import json
import os
import webapp2
import hashlib
from datetime import datetime

from google.appengine.api import (memcache,
                                  mail)
from google.appengine.ext import db

import geo
import hashing
from utils import is_development_env
from models import (Art,
                    Blog,
                    ResetToken,
                    User)
from repositories import (UserRepository,
                          TokenRepository,
                          BlogRepository)
import validation


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def format_datetime(datetime):
    return datetime.strftime("%c")


def allow_linebreaks(content):
    return content.replace("\n", "<br>")

jinja_env.filters['datetime'] = format_datetime
jinja_env.filters['linebreaks'] = allow_linebreaks


class Handler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    # only render page if valid user_id cookie exists
    # otherwise redirect to signup page
    def render_secure(self, template, **kwargs):
        hashed_user_id = self.request.cookies.get('user_id')
        try:
            if hashed_user_id and hashing.check_secure_val(hashed_user_id):
                self.write(self.render_str(template, **kwargs))
            else:
                self.redirect("/login")
        except ValueError:
            self.redirect("/login")


class SignupHandler(Handler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.render("signup.html")

    def post(self):

        kwargs = {}

        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        new_username = UserRepository.username_not_taken(username)
        valid_username = validation.valid_username(username)
        valid_password = validation.valid_password(password)
        valid_verify = (verify == password)
        valid_email = True
        if email:
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
            # use ip address to find lat/lon
            coords = geo.get_coords(self.request.remote_addr)
            if coords:
                new_user.coords = coords
            coords = geo.get_coords(self.request.remote_addr)
            n = new_user.put()
            user_id = n.id()

            # create cookie using hashed id
            hashed_cookie = hashing.make_secure_val(user_id)
            self.response.headers.add_header('Set-Cookie',
                                             'user_id={}; '
                                             'Path=/'.format(hashed_cookie))
            self.redirect("/")


class LoginHandler(Handler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        invalid_reset = self.request.get('invalid_reset')
        self.render("login.html", invalid_reset=invalid_reset)

    def post(self):

        kwargs = {}

        username = self.request.get('username')
        password = self.request.get('password')

        kwargs['username'] = username
        user_id = UserRepository.user_id_from_username_password(username,
                                                                password)
        if not user_id:
            kwargs['invalid'] = "Invalid Login"
            self.render("login.html", **kwargs)
        else:
            # create cookie useing hashed id
            cookie = hashing.make_secure_val(user_id)
            self.response.headers.add_header('Set-Cookie',
                                             'user_id={}; '
                                             'Path=/'.format(cookie))
            self.redirect("/")


class ResetHandler(Handler):

    def send_email(self, username, email, reset_hash):

        if is_development_env():
            base_url = "http://localhost:8080/reset/"
        else:
            base_url = "http://created-by-rachel.appspot.com/reset/"
        url = base_url + reset_hash
        sender_mail = "admin@created-by-rachel.appspotmail.com"
        message = mail.EmailMessage(sender="Rachel's App Support <{}>".
                                           format(sender_mail),
                                    subject="Password Reset for {}".
                                            format(username))
        message.to = "Rachel Thomas <{}>".format(email)
        message.body = """
        Dear {name}:

        We are delighted to reset your password for you.  Please follow
        this link within the next 12 hours:

        {link}

        Thank you for your continued usage of our popular service.

        *** This is an automatically generated email, please do not reply
        to this message ***

        Warmest Regards,
        The 1-person team at created-by-rachel

        """.format(name=username, link=url)

        message.send()

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        invalid = self.request.get('invalid')
        self.render("reset.html", invalid=invalid)

    def post(self):

        kwargs = {}

        entry = self.request.get('entry')
        kwargs['entry'] = entry

        if entry:
            response = UserRepository.email_from_username(entry)
            if response:
                username = entry
                email = response
            else:
                response = UserRepository.username_from_email(entry)
                if response:
                    username = response
                    email = entry

            if response:
                time_created = datetime.now()
                hash_str = username + time_created.strftime("%c")
                name_time_hash = hashlib.sha256(hash_str).hexdigest()
                reset_token = ResetToken(username=username,
                                         time_created=time_created,
                                         name_time_hash=name_time_hash,
                                         active=True)
                reset_token.put()
                self.send_email(username, email, name_time_hash)
            else:
                    kwargs["invalid"] = "That is not a valid username or email"
        else:
            kwargs["invalid"] = "You must enter a username or email"
        self.render("reset_message.html", **kwargs)


class ResetLinkHandler(Handler):

    def get(self, reset_hash):
        self.response.headers['Content-Type'] = 'text/html'
        reset_token = TokenRepository.token_from_hash(reset_hash)
        if reset_token and reset_token.is_valid():
            self.render("reset_password.html", reset_hash=reset_hash)
        else:
            self.redirect("/login?invalid_reset=true")

    def post(self, reset_hash):

        kwargs = {}

        password = self.request.get('password')
        verify = self.request.get('verify')
        reset_token = TokenRepository.token_from_hash(reset_hash)
        if reset_token and reset_token.is_valid():
            username = reset_token.username
            user = UserRepository.user_from_username(username)

            valid_password = validation.valid_password(password)
            valid_verify = (verify == password)

            if not valid_password:
                kwargs['password_error'] = "That wasn't a valid password"
            if not valid_verify:
                kwargs['verify_error'] = "Your passwords didn't match"

            error_dict = {'password_error',
                          'verify_error',
                          }

            # check if any error messages are in kwargs
            if error_dict & set(kwargs.keys()) != set():
                kwargs['reset_hash'] = reset_hash
                self.render("reset_password.html", **kwargs)
            else:
                # set ResetToken to inactive now that it's been used
                reset_token.set_used()
                reset_token.put()
                # salt and hash password
                password_hash_salt = hashing.make_pw_hash(username, password)
                # update user
                user.password_hash_salt = password_hash_salt
                n = user.put()
                user_id = n.id()
                # create cookie using hashed id
                cookie = hashing.make_secure_val(user_id)
                self.response.headers.add_header('Set-Cookie',
                                                 'user_id={}; '
                                                 'Path=/'.format(cookie))
                self.redirect("/")
        else:
            self.redirect('/login?invalid_reset=True')


class LogoutHandler(Handler):

    def get(self):
        self.response.delete_cookie('user_id')
        self.redirect('/login')


class WelcomeHandler(Handler):

    def get(self):
        hashed_user_id = self.request.cookies.get('user_id')
        if hashed_user_id:
            user_id = hashing.check_secure_val(hashed_user_id)
            try:
                user = User.get_by_id(int(user_id))
                self.response.headers['Content-Type'] = 'text/html'
                users = db.GqlQuery("SELECT * FROM User ")
                users = list(users)
                coordinates = filter(None, (a.coords for a in users))
                img_url = None
                if coordinates:
                    img_url = geo.gmaps_img(coordinates)
                self.render_secure("welcome.html", username=user.username,
                                   img_url=img_url)
            except (TypeError,
                    AttributeError):
                self.redirect("/login")
        else:
            self.redirect("/login")


class FlushCacheHandler(Handler):

    def get(self):
        memcache.flush_all()
        self.redirect('/blog')


class BlogMainHandler(Handler):

    def render_blog_main_page(self):
        blog_posts, cache_age = BlogRepository.get_blog_posts()
        self.render_secure("blog.html",
                           blog_posts=blog_posts,
                           cache_age=cache_age)

    def get(self):
        self.render_blog_main_page()


class BlogJSONHandler(Handler):

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        blog_posts, cache_age = BlogRepository.get_blog_posts()
        blog_json = [Blog.get_json(b) for b in blog_posts]
        self.write(json.dumps(blog_json))


class PermalinkJSONHandler(Handler):

    def get(self, blog_id):
        self.response.headers['Content-Type'] = 'application/json'
        blog = Blog.get_by_id(int(blog_id))
        blog_json = Blog.get_json(blog)
        self.write(json.dumps(blog_json))


class NewPostHandler(Handler):

    def render_new_post(self, subject="", content="", error=""):
        self.render_secure("newpost.html",
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
            BlogRepository.put(new_blog_post)
            self.redirect("/blog/"+str(new_blog_post.key().id()))
        else:
            error = "we need both a subject and content!"
            self.render_new_post(subject=subject, content=content, error=error)


class PermalinkHandler(Handler):

    def get(self, blog_id):
        blog, cache_age = BlogRepository.get_blog_by_id(blog_id)
        self.render_secure("permalink.html", blog=blog, cache_age=cache_age)


class MainHandler(Handler):

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


class AsciiHandler(Handler):

    def render_ascii(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art "
                           "ORDER BY created DESC "
                           "LIMIT 10")
        arts = list(arts)

        self.render_secure("ascii.html", title=title, art=art, error=error,
                           arts=arts)

    def get(self):
        # self.write(repr(get_coords(self.request.remote_addr)))
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


app = webapp2.WSGIApplication([('/blog/?', BlogMainHandler),
                              ('/blog/newpost', NewPostHandler),
                              ('/blog/(\d+)', PermalinkHandler),
                              ('/blog/(\d+)/?\.json', PermalinkJSONHandler),
                              ('/blog/?\.json', BlogJSONHandler),
                              ('/blog/flush/?', FlushCacheHandler),
                              ('/reset/(\w+)', ResetLinkHandler),
                              ('/reset', ResetHandler),
                              ('/ascii', AsciiHandler),
                              ('/signup', SignupHandler),
                              ('/login', LoginHandler),
                              ('/logout', LogoutHandler),
                              ('/', WelcomeHandler)],
                              debug=True
                              )
