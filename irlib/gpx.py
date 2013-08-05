"""
GPX IO and manipulation (UNDER DEVELOPMENT)

This is a rewrite of gpxparser.py, designed to fit better with guppy types.

To do:
    - XML namespaces aren't really handled properly
    - metadata node not addressed
"""

import sys
import collections
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ElementTree, Element
from xml.dom import minidom

Point = collections.namedtuple("Point", ["lonlat", "properties", "extensions"])
Trkseg = collections.namedtuple("Trkseg", ["trkpts", "properties", "extensions"])
Track = collections.namedtuple("Track", ["trksegs", "properties", "extensions"])
Route = collections.namedtuple("Route", ["rtepts", "properties", "extensions"])

ns = "{http://www.topografix.com/GPX/1/1}"

def strip_namespace(s):
    return s[s.index("}")+1:]

class GPX(object):
    """ Represents a GPX document, with an internal representation of
    waypoints, tracks, and route that loosely approximates the XML structure.
    Provides methods to easily add Point-like and Line-like objects as GPX
    types. """

    def __init__(self, f=None, waypoints=None, tracks=None, routes=None):
        """ Create a GPX object, either from a GPX file or from lists of
        waypoints, tracks, and routes. """

        self.waypts = {}
        self.tracks = {}
        self.routes = {}

        if f is not None:
            self.fromfile(f)

        else:
            if waypoints is not None:
                for waypt in waypoints:
                    self.add_waypoint(waypt)
            if tracks is not None:
                for track in tracks:
                    self.add_track(track)
            if routes is not None:
                for route in routes:
                    self.add_route(route)
        return

    def _readextensions(self, node):
        extensions = {}
        for ext in node.find("extensions"):
            extensions[strip_namespace(ext.tag)] = ext.text
        return extensions

    def _readproperties(self, node, exclude=()):
        properties = {}
        for node in wpt:
            tag = strip_namespace(node.tag)
            if tag not in exclude:
                properties[tag] = node.text
        return properties

    def _readwpt(self, wpt):
        properties = self._readproperties(wpt, exclude=("extensions",))
        extensions = self._readextensions(wpt)
        lon = wpt.attrib["lon"]
        lat = wpt.attrib["lat"]
        return Point((lon, lat), properties, extensions)

    def _dict2gpx(self, parent, properties):
        for p in properties:
            sub = Element(ns + p)
            sub.text = str(properties[p])
            parent.append(sub)
        return parent

    def _extensions2gpx(self, parent, extensions):
        ext = Element(ns + "extensions")
        ext = self._dict2gpx(ext, extensions)
        parent.append(ext)
        return parent

    def _build_gpx_wpt(self, waypt, tag="wpt"):
        """ Build <wpt> node. """
        wpt = Element(ns + tag, lon=str(waypt.lonlat[0]), lat=str(waypt.lonlat[1]))
        wpt = self._dict2gpx(wpt, waypt.properties)
        wpt = self._extensions2gpx(wpt, waypt.extensions)
        return wpt

    def _build_gpx_trk(self, track):
        """ Build "trk" nodes. """
        trk = Element(ns + "trk")
        trk = self._dict2gpx(trk, track.properties)
        trk = self._extensions2gpx(trk, track.extensions)

        for segment in track.trksegs:
            trkseg = Element(ns + "trkseg")
            trkseg = self._dict2gpx(trkseg, segment.properties)
            trkseg = self._extensions2gpx(trkseg, segment.extensions)

            for trackpt in segment.trkpts:
                trkpt = self._build_gpx_wpt(trackpt, tag="trkpt")
                trkseg.append(trkpt)

            trk.append(trkseg)
        return trk

    def _build_gpx_rte(self, route):
        rte = Element(ns + "rte")
        rte = self._dict2gpx(rte, route.properties)
        rte = self._extensions2gpx(rte, route.extensions)
        for routept in route.rtepts:
            rte.append(self._build_gpx_wpt(routept, tag="rtept"))
        return rte

    def fromfile(self, f):
        """ Read a GPX document from *f*, which may be a filename or a
        file-like object. """

        gpxtree = ElementTree(file=f)
        self.gpx = gpxtree.getroot()

        for node in self.gpx.findall(ns + "wpt"):
            self.parse_wpt(node)

        for node in self.gpx.findall(ns + "trk"):
            self.parse_trk(node)

        for node in self.gpx.findall(ns + "rte"):
            self.parse_rte(node)

        return

    def parse_wpt(self, wpt):
        """ Parse a <wpt> node, updating self.waypoints. """
        point = self._readwpt(wpt)
        name = wpt.properties.get("name", "waypoint_" + str(len(self.waypoints)))
        self.waypoints[name] = point
        return

    def parse_trk(self, trk):
        """ Parse a <trk> node, updating self.tracks. """
        name = trk.get("name", "route_" + str(len(self.tracks)))
        segments = []

        for trkseg in trk.findall(ns + "trkseg"):

            points = [self._readwpt(trkpt) for trkpt in trkseg.findall(ns + "trkpt")]
            properties = self._readproperties(trkseg, exclude=("trkpt",))
            extensions = self._readextensions(trkseg)
            segments.append(Trkseg(points, properties, extensions))

        self.tracks[name] = Track(segments, name)
        return

    def parse_rte(self, rte):
        properties = self._readproperties(rte, exclude=("rtept",))
        extensions = self._readextensions(rte)
        name = properties.get("name", "route_" + str(len(self.routes)))
        points = [self._readwpt(rtept) for rtept in rte.findall(ns + "rtept")]
        self.routes[name] = Route(points, properties, extensions)
        return

    def add_waypoint(self, waypoint):
        """ Add a Point-like object as a waypoint. Properties and extension
        types are taken from waypoint.properties attribute. """
        waypt = Point(waypoint.vertex, properties, {})
        name = waypt.properties.get("name", "waypt_" + len(self.waypoints))
        self.waypoints[name] = waypt
        return

    def add_track(self, track, properties=None, extensions=None):
        """ Add a list of Line-like objects as a track. Dictionaries of
        properties and extension types for the track are accepted as keyword
        arguments.

        Properties and extension types for the track segments are taken from
        the `properties` attribute of each Line-like object.

        Properties and extensions types for each track point are taken from the
        `data` attribute of each Line-like object.

        INCOMPLETE:

        Needs to distinguish between properties and extensions at the trkseg
        and trkpt levels

        Needs to properly add and <ele> property for Lines of rank 3
        """
        for line in track:
            points = []
            for i, vertex in enumerate(line.vertices):
                prop = {}
                for k in line.data.keys():
                    prop[k] = line.data[k][i]
                points.append(Point((vertex[0], vertex[1]), prop, {}))
            segment = Trkseg(points, line.properties, {})
        name = properties.get("name", "track_" + len(self.tracks))
        self.track[name] = Track(segements, properties, extensions)
        return

    def add_route(self, route):
        """ Add a list of Line-like objects as a route. Properties and
        extension types for the route are taken from the `properties` attribute
        of the Line-like object.

        Properties and extensions types for each route point are taken from the
        `data` attribute of each Line-like object.

        INCOMPLETE:

        Needs to distinguish between properties and extensions at the trkseg
        and trkpt levels

        Needs to properly add and <ele> property for Lines of rank 3
        """
        points = []
        for i, vertex in enumerate(route.vertices):
            prop = {}
            for k in route.data.keys():
                prop[k] = route.data[k][i]
            points.append(Point((vertex[0], vertex[1]), prop, {}))
        route = Route(points, route.properties, {})
        name = route.properties.get("name", "route_" + len(self.routes))
        self.route[name] = route
        return

    def writefile(self, fnm, waypts=True, tracks=True, routes=True):
        """ Write GPX object to a GPX file. Writes all waypoints, tracks, and
        routes by default, which can be changed by changing the kwargs to
        False. """
        gpx = Element(ns + "gpx", version="1.1", creator="karta")

        if waypts:
            for waypt in self.waypts.values():
                gpx.append(self._build_gpx_wpt(waypt))
        if tracks:
            for track in self.tracks.values():
                gpx.append(self._build_gpx_trk(track))
        if routes:
            for route in self.routes.values():
                gpx.append(self._build_gpx_rte(route))

        xmlstring = ET.tostring(gpx)
        output = minidom.parseString(xmlstring).toprettyxml(indent="  ")
        with open(fnm, "w") as f:
            f.write(output)
        return

