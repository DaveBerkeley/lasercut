
import math

from laser import Polygon, Arc, Collection, rotate_2d, radians

from shapely.geometry import MultiPolygon
from shapely.geometry import Polygon as sPolygon

#
#

min_line = 2.0

def arc_to_poly(arc):
    # Have to convert arc into line segments
    point = 0, arc.radius
    circ = math.pi * arc.radius
    divs = circ / min_line
    div = 360.0 / divs

    poly = Polygon()
    poly.add(0, 0)
    angle = arc.start_angle
    while angle <= arc.end_angle:
        x, y = rotate_2d(radians(angle), *point)
        x, y = x + arc.x, y + arc.y
        poly.add(x, y)
        angle += div
    poly.close()

    return poly

def to_shape(obj):
    polys = []
    def nest(obj):
        if isinstance(obj, Collection):
            for d in obj.data:
                nest(d)
        elif isinstance(obj, Polygon):
            p = sPolygon(obj.points[:])
            polys.append(p)
            for arc in obj.arcs:
                nest(arc)
        elif isinstance(obj, Arc):
            nest(arc_to_poly(obj))
        else:
            raise Exception(("shape not supported", obj))
    nest(obj)
    return MultiPolygon(polys)

#
#

def from_shape(sh):
    c = Collection()

    p = Polygon()
    for point in sh.exterior.coords:
        p.add(*point)
    c.add(p)

    for seq in sh.interiors:
        p = Polygon()
        for point in seq.coords:
            p.add(*point)
        c.add(p)

    return c

#
#

class Shape:

    def __init__(self, obj=None, shape=None):
        self.shape = shape or to_shape(obj)
    def get(self):
        return from_shape(self.shape)
    def union(self, shape):
        u = self.shape.union(shape.shape)
        return Shape(shape=u)
    def intersection(self, shape):
        u = self.shape.intersection(shape.shape)
        return Shape(shape=u)
    def symmetric_difference(self, shape):
        u = self.shape.symmetric_difference(shape.shape)
        return Shape(shape=u)

#   FIN
