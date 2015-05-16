
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
    # assume multilinestring
    c = Collection()
    p = Polygon()
    for point in sh.exterior.coords:
        p.add(*point)
    c.add(p)
    return c

#
#

def binary(p1, p2, op):
    sh1 = to_shape(p1)
    sh2 = to_shape(p2)
    fn = getattr(sh1, op)
    u = fn(sh2)
    return from_shape(u)    

def union(p1, p2):
    return binary(p1, p2, "union")

def intersection(p1, p2):
    return binary(p1, p2, "intersection")

#   FIN
