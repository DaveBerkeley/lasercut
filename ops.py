
from laser import Polygon, Arc, Collection

from shapely.geometry import LineString, MultiLineString, MultiPolygon
from shapely.geometry import Polygon as sPolygon

#
#

def to_shape(obj):
    polys = []
    def nest(obj):
        if isinstance(obj, Collection):
            for d in obj.data:
                nest(d)
        elif isinstance(obj, Polygon):
            p = sPolygon(obj.points[:])
            polys.append(p)
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
