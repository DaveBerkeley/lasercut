#!/usr/bin/python

import sys
import math

from laser import Arc, Circle, Polygon, Collection, Config
from laser import radians, degrees
from render import DXF as dxf

#
#

axial_tilt = 23.43721
latitude = 40.0 # 52.0

def project_1(angle):
    A = angle + (90.0 - latitude)
    a = math.cos(radians(A))
    b = math.sin(radians(A))

    x = -a / (b + 1)
    return x

def project(angle):
    x1 = project_1(angle)
    x2 = project_1(180.0 - angle)
    mid = (x1 + x2) / 2.0
    r = abs((x2 - x1) / 2.0)
    return mid, r

#
#   Equations from "The Astrolabe" by James E Morrison.

def r_eq(r_cap, e=axial_tilt):
    # radius of equator, given radius of tropic of capricorn
    return r_cap * math.tan(radians((90.0 - e) / 2.0))

def r_can(r_eq, e=axial_tilt):
    # radius of tropic of cancer, given the equator
    return r_eq * math.tan(radians((90.0 - e) / 2.0))

#
#

def intersect(x0, r0, x1, r1):
    y0, y1 = 0, 0
    # http://paulbourke.net/geometry/circlesphere/
    dx = x1 - x0
    dy = y1 - y0

    d = math.sqrt((dy*dy) + (dx*dx))

    if d > (r0 + r1): # seperate
        return None
    if d < abs(r0 - r1): # nested
        return None
    if (d == 0) and (r0 == r1): # co-incident
        return None

    a = ((r0*r0) - (r1*r1) + (d*d)) / (2 * d)

    x2 = x0 + (dx * (a/d))
    y2 = y0 + (dy * (a/d))

    h = math.sqrt((r0*r0) - (a*a))

    rx = -dy * (h/d)
    ry = dx * (h/d)

    xi = x2 + rx
    xii = x2 - rx
    yi = y2 + ry
    yii = y2 - ry

    return xi, yi, xii, yii

#
#

class Circ:

    def __init__(self, x, r):
        self.x = x
        self.r = r

    def shape(self, s=1.0):
        return Circle((self.x * s, 0), self.r * s)

    def intersect(self, c):
        return intersect(self.x, self.r, c.x, c.r)

#
#

def ticks(work, xy, r1, r2, a1, a2, step):
    a = a1
    assert a1 <= a2
    while a <= a2:
        p = Polygon()
        x = math.sin(radians(a))
        y = math.cos(radians(a))
        p.add(r1 * x, r1 * y)
        p.add(r2 * x, r2 * y)
        work.add(p)
        a += step

#
#

def old():
    s = 100

    config = Config()
    work = Collection()

    drawing = dxf.drawing("test.dxf")

    unit = Circ(0, 1)
    c = unit.shape(s)
    work.add(c)

    for a in range(0, 91, 5):
        print a,
        m, r = project(a)
        #print a, m, r
        cc = Circ(m, r)
        ii = cc.intersect(unit)
        if ii:
            x0, y0, x1, y1 = ii

            x = x0 - m
            y = y0
            a = degrees(math.atan2(y, x))
            x = x1 - m
            y = y1
            b = degrees(math.atan2(y, x))
            print a, b

            arc = Arc((s * m, 0), s * r, b, a)
            work.add(arc)
        else:
            c = cc.shape(s)
            work.add(c)

    #m, r = project(-5)
    #tropic = Circ(0, m)
    #c = tropic.shape(s)
    #work.add(c)
    #m, r = project(-axial_tilt)
    #tropic = Circ(0, m)
    #c = tropic.shape(s)
    #work.add(c)

    xy = 0, 0
    outer = 1.05 * s
    inner = 1.2 * s
    mid = 1.15 * s
    ticks(work, xy, mid, outer, 0, 360, 360 / 24.0)
    ticks(work, xy, inner, mid, 0, 360, 360 / 120.0)
    c = Circle(xy, inner)
    work.add(c)
    c = Circle(xy, mid)
    work.add(c)
    c = Circle(xy, outer)
    work.add(c)

    work.draw(drawing, config.cut())

    drawing.save()

#
#

def astrolabe():
    s = 100

    config = Config()
    work = Collection()

    drawing = dxf.drawing("test.dxf")

    # equator and tropics
    rad_cap = s
    rad_eq = r_eq(rad_cap)
    rad_can = r_can(rad_eq)

    for r in [ rad_cap, rad_eq, rad_can ]:
        circ = Circ(0, r)
        c = circ.shape()
        work.add(c)

    work.draw(drawing, config.engrave_colour)

    drawing.save()
    print dir(config)

#
#

if __name__ == "__main__":
    astrolabe()

# FIN
