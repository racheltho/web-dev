import webapp2

from validation import (valid_day,
                        valid_month,
                        valid_year)

form = """
<form method="post" action="/">
    Enter your birth day:
    <label>Month <input name="month" value={month}></label>
    <label>Day <input name="day" value={day}></label>
    <label>Year <input name="year" value={year}></label>
    <div style="color: red">{error}</div>
    <br>
    <br><input type="submit">
    &amp;=&amp;amp;
</form>
"""


class MainPage(webapp2.RequestHandler):

    def write_form(self, error="", month="", day="", year=""):
        self.response.out.write(form.format(error=error,
                                            month=month,
                                            day=day,
                                            year=year
                                            ))

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.write_form()

    def post(self):
        user_month = valid_month(self.request.get('month'))
        user_day = valid_day(self.request.get('day'))
        user_year = valid_year(self.request.get('year'))

        if not (user_month and user_day and user_year):
            self.write_form("Invalid input",
                            user_month,
                            user_day,
                            user_year)
        else:
            self.response.out.write("Thanks! That's a valid day!")


app = webapp2.WSGIApplication([('/', MainPage)],
                              debug=True)
