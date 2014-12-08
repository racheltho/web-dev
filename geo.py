import urllib2
from xml.dom import minidom
from google.appengine.ext import db


IP_URL = "http://api.hostip.info/?ip="
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"


def get_coords(ip):
    ip = "203.26.235.14"
    # ip = "4.2.2.2"
    url = IP_URL + ip
    content = None
    try:
        content = urllib2.urlopen(url).read()
    except urllib2.URLError:
        return
    if content:
        xml = minidom.parseString(content)
        xml_coords = xml.getElementsByTagName("gml:coordinates")
        if xml_coords:
            child = xml_coords[0].childNodes
            if child:
                lon, lat = child[0].nodeValue.split(",")
                return db.GeoPt(lat, lon)


def gmaps_img(points):
    markers = "&".join("markers={},{}".format(p.lat, p.lon) for p in points)
    return GMAPS_URL + markers
