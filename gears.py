#!/usr/bin/python

import math

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Polygon, Circle, Collection, Config
from laser import radians, rotate_2d

# Involute gears, see :
# http://www.cartertools.com/involute.html

def scale(a):
    return a * 254

#
#

def make_involute(P, N, PA=14.5):
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
        "outside_dia" :  scale(DO),
        "pitch_dia" : scale(D),
        "root_dia" : scale(DR),
    }

    work = Collection()
    work.info = info
    v = Polygon()
    v.add(0, scale(RR))

    # note : the range 5 .. 12 approximates to the intersection
    # with the D and DO circles
    for i in range(5, 12):
        x, y = i * RB / 20.0, RB
        x, y = [ scale(z) for z in [ x, y ] ]
        x, y = rotate_2d(radians(i * acb), x, y)
        v.add(x, y)

    # rotate back 1/4 tooth
    v.rotate(-gt / 4.0)
    # add reflection to itself
    w = v.copy()
    w.reflect_v()
    # make sure the halves are joined correctly
    w.points.reverse()
    v.add_poly(w)

    prev = None
    first = None

    for i in range(N):
        c = v.copy()
        c.rotate(gt * i)
        work.add(c)
        # join the last 2 teeth together
        se = c.points[0], c.points[-1]
        if not prev is None:
            p = Polygon()
            p.add(*prev[1])
            p.add(*se[0])
            work.add(p)
        if first is None:
            first = se
        prev = c.points[0], c.points[-1]

    # join the first and last gears together
    p = Polygon()
    p.add(*prev[1])
    p.add(*first[0])
    work.add(p)
    return work

#
#

if __name__ == "__main__":
    x_margin = 10
    y_margin = 20

    def commit(work):
        #work.translate(x_margin, y_margin)
        work.draw(drawing, config.cut())

    config = Config()

    drawing = dxf.drawing("test.dxf")

    P = 16.0
    N = 20
    PA = 14.5

    work = make_involute(P, N, PA)

    for label in [ "outside_dia", "root_dia", "pitch_dia" ]:
        d = work.info[label]
        c = Circle((0, 0), d / 2.0, colour=Config.draw_colour)
        work.add(c)

    commit(work)

    drawing.save()

# FIN
