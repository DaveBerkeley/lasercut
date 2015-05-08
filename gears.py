#!/usr/bin/python

import sys
import math

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Polygon, Circle, Collection, Config
from laser import radians, rotate_2d

# Involute gears, see :
# http://www.cartertools.com/involute.html

#
#

def circle_intersect(v, r):
    # see http://mathworld.wolfram.com/Circle-LineIntersection.html
    x1, y1 = v.points[-2]
    x2, y2 = v.points[-1]
    dx = x1 - x2
    dy = y1 - y2
    dr = math.sqrt((dx * dx) + (dy * dy))
    D = (x1 * y2) - (x2 * y1)
    def sgn(a):
        return -1
    x = -((D * dy) - (sgn(dy)*dx*math.sqrt(((r*r)*(dr*dr))-(D*D)))) / (dr*dr)
    y = -((-D*dx) - (abs(dy)* math.sqrt(((r*r)*(dr*dr))-(D*D)))) / (dr*dr)

    # truncate the last line segment to fit the radius
    v.points[-1] = x, y

#
#

def make_involute(pitch_dia, N, PA=14.5, teeth=None):
    m = float(pitch_dia) / N
    P = 1.0 / m
    D = N / P                       # Pitch Diameter
    R = D / 2.0                     # Pitch Radius
    DB = D * math.cos(radians(PA))  # Base Circle Diameter
    RB = DB / 2.0                   # Base Circle Radius
    a = 1.0 / P                     # Addendum
    d = 1.157 / P                   # Dedendum
    DO = D + (2 * a)                # Outside Diameter
    RO = DO / 2.0                   # Outside Radius
    DR = D - (2 * d)                # Root Diameter
    RR = DR / 2.0                   # Root Radius

    CB = math.pi * DB               # Circumference of Base Circle
    fcb = RB / 20.0
    ncb = CB / fcb
    acb = 360 / ncb
    gt = 360.0 / N                  # Gear Tooth Spacing

    info = {
        "outside_dia" :  DO,
        "pitch_dia" : D,
        "root_dia" : DR,
    }

    v = Polygon()
    v.add(0, RR)

    # note : the range 5 .. 12 approximates to the intersection
    # with the D and DO circles
    for i in range(5, 12):
        x, y = i * RB / 20.0, RB
        x, y = rotate_2d(radians(i * acb), x, y)
        v.add(x, y)

    # need to trim last involute line segment
    # so it doesn't exceed the outside_radius
    circle_intersect(v, RO)

    # rotate back 1/4 tooth
    v.rotate(-gt / 4.0)
    # add reflection to itself
    w = v.copy()
    w.reflect_v()
    # make sure the halves are joined correctly
    w.points.reverse()
    v.add_poly(w)

    work = Polygon()
    work.info = info
    # add all the teeth to the work
    for i in range(teeth or N):
        c = v.copy()
        c.rotate(gt * i)
        work.add_poly(c)

    # join the ends together
    if teeth is None:
        work.close()
    return work

#
#

if __name__ == "__main__":
    x_margin = 10
    y_margin = 20

    draw = False

    if len(sys.argv) > 1:
        draw = True

    def commit(work):
        #work.translate(x_margin, y_margin)
        work.draw(drawing, config.cut())

    config = Config()

    drawing = dxf.drawing("test.dxf")

    N = 20
    PA = 14.5
    pitch_dia = 20
    nteeth = None # 6 # set if only some teeth required

    work = make_involute(pitch_dia, N, PA, teeth=nteeth)

    if nteeth:
        work.add(0, 0)
        work.close()

    if draw:
        for label in [ "outside_dia", "root_dia", "pitch_dia" ]:
            d = work.info[label]
            c = Circle((0, 0), d / 2.0, colour=Config.draw_colour)
            work.add(c)

    commit(work)

    drawing.save()

# FIN
