#!/usr/bin/python

from laser import Config, Polygon, Rectangle, Circle, Collection
from laser import angle, radians, degrees, rotate_2d

from gears import make_involute

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#   Compensate for kerf

def parallel(xy0, xy1, kerf, inner):
    x0, y0 = xy0
    x1, y1 = xy1
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

def dekerf(poly, kerf, inner):
    # assert Polygon
    work = Collection()
    for i in range(len(poly.points)-1):
        xy0, xy1 = parallel(poly.points[i], poly.points[i+1], kerf, inner)
        print xy0, xy1
        #print eol(xy0, xy1)
        p = Polygon(colour=Config.draw_colour)
        p.add(*xy0)
        p.add(*xy1)
        work.add(p)
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
    commit(work)

    kerf = 1 # 0.2
    work = dekerf(work.copy(), kerf, False)
    commit(work)

    drawing.save()

# FIN
