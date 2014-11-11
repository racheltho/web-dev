months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']


def valid_month(month):
    try:
        cased_month = month[0].upper() + month[1:].lower()
    except IndexError:
        return None
    if cased_month in months:
        return cased_month


def valid_day(day):
    try:
        day_int = int(day)
    except ValueError:
        return None
    if day_int in range(1, 32):
        return day_int


def valid_year(year):
    try:
        year_int = int(year)
    except ValueError:
        return None
    if year_int in range(1900, 2021):
        return year_int
