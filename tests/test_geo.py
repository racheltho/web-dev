import unittest
from google.appengine.ext import db

from geo import (get_coords,
                 gmaps_img)


class TestGeo(unittest.TestCase):
    def test_get_coords(self):
        ip = "203.26.235.14"
        assert get_coords(ip) == db.GeoPt(-37.824, 144.973)

    def test_gmaps_img(self):
        test_points = [db.GeoPt(1, 2), db.GeoPt(3,4)]
        maps_string = ("http://maps.googleapis.com/maps/api/staticmap?"
                       "size=380x263&sensor=false&markers=1.0,2.0&markers=3.0,4.0")
        assert gmaps_img(test_points) == maps_string
