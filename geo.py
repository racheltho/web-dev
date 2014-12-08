import urllib2
import httplib
import os
from xml.dom import minidom
from google.appengine.ext import db


IP_URL = "https://freegeoip.net/xml/"
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"


def is_development_env():
    return os.environ['SERVER_SOFTWARE'].startswith('Development')


def get_coords(ip):
    if is_development_env():
        ip = "203.26.235.14"
    url = IP_URL + ip
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return
    except httplib.HTTPException:
        return
    if content:
        xml = minidom.parseString(content)
        xml_lat = xml.getElementsByTagName("Latitude")
        xml_lon = xml.getElementsByTagName("Longitude")
        if xml_lat and xml_lon:
            lat = xml_lat[0].childNodes[0].nodeValue
            lon = xml_lon[0].childNodes[0].nodeValue
            # return lat, lon
            return db.GeoPt(lat, lon)


def gmaps_img(points):
    markers = "&".join("markers={},{}".format(p.lat, p.lon) for p in points)
    return GMAPS_URL + markers
