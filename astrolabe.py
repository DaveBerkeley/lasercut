#!/usr/bin/python

import sys
import math

from laser import Arc, Circle, Polygon, Collection, Config, Text
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

def draw_almucantar(a, colour, work, rad_eq, outer):
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


def plate(drawing, config, size):
    s = size

    work = Collection()

    # equator and tropics
    rad_cap = s
    rad_eq = r_eq(rad_cap)
    rad_can = r_can(rad_eq)

    outer = Circ(0, rad_cap)
    c = outer.shape(colour=config.cut())
    work.add(c)

    circ = Circ(0, rad_eq)
    c = circ.shape(colour=config.thick_colour)
    work.add(c)

    circ = Circ(0, rad_can)
    c = circ.shape(colour=config.thick_colour)
    work.add(c)

    # quarters
    p = Polygon(colour=config.thick_colour)
    p.add(-s, 0)
    p.add(s, 0)
    work.add(p)

    p = Polygon(colour=config.thick_colour)
    p.add(0, -s)
    p.add(0, s)
    work.add(p)

    # draw the almucantar lines
    for a in range(0, 90, 2):
        colour = config.thin_colour
        if (a % 10) == 0:
            colour = config.thick_colour
        draw_almucantar(a, colour, work, rad_eq, outer)

    # twilight arcs
    if 1:
        colour = config.dotted_colour
        nautical_twilight = -12
        civil_twilight = -6
        astronomical_twilight = -18
        for twilight in [ nautical_twilight, civil_twilight, astronomical_twilight ]:
            draw_almucantar(twilight, colour, work, rad_eq, outer)

    # azimuth lines
    if 0:
        yz =  rad_eq * math.tan(radians(90.0 - latitude) / 2.0)
        yn = -rad_eq * math.tan(radians(90.0 + latitude) / 2.0)
        yc = (yz + yn) / 2.0
        yaz = (yz - yn) / 2.0
        for angle in range(0, 180, 15):
            if angle in [ 90 ]:
                continue
            xa = yaz * math.tan(radians(angle))
            ra = yaz / math.cos(radians(angle))
            print xa, ra
            c = Circle((yc, xa), ra)
            work.add(c)

    work.draw(drawing, config.thick_colour)

#
#

def mater(drawing, config, size):
    work = Collection()
    inner = size * 1.01
    outer = size * 1.2
    mid = (inner + outer) / 2
    small = (mid + outer) / 2

    # draw ticks
    ticks(work, (0, 0), inner, outer, 0, 360, 15)
    ticks(work, (0, 0), mid, outer, 0, 360, 3)
    ticks(work, (0, 0), small, outer, 0, 360, 1)

    # draw / cut circles
    c = Circle((0, 0), inner, colour=config.cut())
    work.add(c)
    c = Circle((0, 0), mid, colour=config.thick_colour)
    work.add(c)
    c = Circle((0, 0), outer, colour=config.cut())
    work.add(c)

    hours = [ 
        "I", "II", "III", "IIII", "V", "VI", 
        "VII", "VIII", "IX", "X", "XI", "XII", 
    ] 
    # label the limb
    for idx, a in enumerate(range(0, 360, 15)):
        rad = radians(a)

        if a > 270:
            label = 360 - a
        elif a > 180:
            label = a - 180
        elif a > 90:
            label = 180 - a
        else:
            label = a

        # degrees
        t = Text((0, 0), "%0.1d" % label, height=size/35.0)
        t.rotate(-a)
        r = small - 1
        x, y = r * math.sin(rad), r * math.cos(rad)
        t.translate(x, y)
        t.rotate(-0.3)
        work.add(t)

        # hours
        t = Text((0, 0), hours[idx % 12], height=size/20.0)
        t.rotate(-a)
        r = mid - 2
        x, y = r * math.sin(rad), r * math.cos(rad)
        t.translate(x, y)
        t.rotate(-90 - 8)
        work.add(t)

    work.draw(drawing, config.thick_colour)

#
#

if __name__ == "__main__":
    drawing = dxf.drawing("test.dxf")
    config = Config()

    size = 100.0
    plate(drawing, config, size)

    mater(drawing, config, size)

    drawing.save()

# FIN
