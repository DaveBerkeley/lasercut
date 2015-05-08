#!/usr/bin/python

from laser import Config, Polygon, Rectangle, Circle, Collection
from laser import angle, radians, degrees, rotate_2d

from gears import make_involute

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#   Compensate for kerf

def parallel(points, kerf, inner):
    x0, y0 = points[0]
    x1, y1 = points[1]
    dx, dy = x1 - x0, y1 - y0
    a = angle(dx, dy)
    # vector at 90 degrees to line
    if inner:
        x, y = rotate_2d(a, 0, kerf)
    else:
        x, y = rotate_2d(a, 0, -kerf)
    return (x0 + x, y0 + y), (x1 + x, y1 + y)

def eol(xy0, xy1):
    x0, y0 = xy0
    x1, y1 = xy1
    dx, dy = x1 - x0, y1 - y0
    m = (y1 - y0) / (x1 - x0)
    return m, y0 - (m * x0) 

def intersect(e0, e1):
    m0, c0 = e0
    m1, c1 = e1
    x = (c0 - c1) / (m1 - m0)
    y = (m0 * x) + c0
    return x, y

def dekerf(poly, kerf, inner):
    # assert Polygon
    work = Polygon(colour=8)

    def line_pairs(points):
        first = None
        while len(points) >= 3:
            l0 = points[:2]
            l1 = points[1:3]
            yield l0, l1
            points = points[1:]
            if first is None:
                first = l0
        yield points, first

    for xy0, xy1 in line_pairs(poly.points[:]):
        xy0 = parallel(xy0, kerf, inner)
        xy1 = parallel(xy1, kerf, inner)
        e0, e1 = eol(*xy0), eol(*xy1)
        x, y = intersect(e0, e1)
        work.add(x, y)
    work.close()
    return work

#
#

if __name__ == "__main__":

    def commit(work):
        work.draw(drawing, config.cut())

    config = Config()

    drawing = dxf.drawing("test.dxf")

    N = 20
    PA = 14.5
    pitch_dia = 20

    #work = make_involute(pitch_dia, N, PA)
    work = Rectangle((0, 0), (10, 10))
    work.rotate(15)
    commit(work)

    kerf = 0.5
    work = dekerf(work.copy(), kerf, False)
    commit(work)

    drawing.save()

# FIN
