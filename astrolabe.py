#!/usr/bin/python

import sys
import math

from laser import Arc, Circle, Polygon, Collection, Config
from laser import radians, degrees
from render import DXF as dxf

#
#

axial_tilt = 23.43721
latitude = 52.0

#
#   Equations from "The Astrolabe" by James E Morrison.

def r_eq(r_cap, e=axial_tilt):
    # radius of equator, given radius of tropic of capricorn
    return r_cap * math.tan(radians((90.0 - e) / 2.0))

def r_can(r_eq, e=axial_tilt):
    # radius of tropic of cancer, given the equator
    return r_eq * math.tan(radians((90.0 - e) / 2.0))

def almucantar(a, req, lat=latitude):
    aa, ll = radians(a), radians(lat)
    ra = req * math.cos(aa) / (math.sin(ll) + math.sin(aa))
    ya = req * math.cos(ll) / (math.sin(ll) + math.sin(aa))
    return ra, ya

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

    def shape(self, s=1.0, **kwargs):
        return Circle((self.x * s, 0), self.r * s, **kwargs)

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

def plate(drawing, config, size):
    s = size

    work = Collection()

    # equator and tropics
    rad_cap = s
    rad_eq = r_eq(rad_cap)
    rad_can = r_can(rad_eq)
    outer = Circ(0, rad_cap)

    for r in [ rad_cap, rad_eq, rad_can ]:
        circ = Circ(0, r)
        c = circ.shape()
        work.add(c)

    for a in range(0, 90, 2):
        colour = config.thin_colour
        if (a % 10) == 0:
            colour = config.thick_colour
        ra, ya = almucantar(a, rad_eq)
        circ = Circ(ya, ra)
        ii = outer.intersect(circ)
        if ii:
            x0, y0, x1, y1 = ii
            m = circ.x

            x = x0 - m
            y = y0

            a = degrees(math.atan2(y, x))
            x = x1 - m
            y = y1
            
            b = degrees(math.atan2(y, x))

            arc = Arc((m, 0), ra, a, b, colour=colour)
            work.add(arc)
        else:
            c = circ.shape(colour=colour)
            c.rotate(radians(90.0))
            work.add(c)

    work.draw(drawing, config.thin_colour)

#
#

if __name__ == "__main__":
    drawing = dxf.drawing("test.dxf")
    config = Config()

    size = 100
    plate(drawing, config, size)
    drawing.save()

# FIN
