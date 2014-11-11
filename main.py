import webapp2
import cgi
from rot13 import rot13_text

form = """
<form method="post" action="/">
    <textarea name="text"
              style="height: 100px; width: 400px;">{text}</textarea>
    <br>
    <br><input type="submit">
</form>
"""


class MainPage(webapp2.RequestHandler):

    def write_form(self, text=""):
        self.response.out.write(form.format(text=text))

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.write_form()

    def post(self):
        text = cgi.escape(rot13_text(self.request.get('text')))
        self.write_form(text)


app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
