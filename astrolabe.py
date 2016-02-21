#!/usr/bin/python

import sys
import math

from laser.laser import Arc, Circle, Polygon, Collection, Config, Text
from laser.laser import radians, degrees
from laser.render import DXF as dxf

#
#

axial_tilt = 23.43721

class Twilight:
    civil = -6
    nautical = -12
    astronomical = -18

#
#   Equations from "The Astrolabe" by James E Morrison.

def r_eq(r_cap, e=axial_tilt):
    # radius of equator, given radius of tropic of capricorn
    return r_cap * math.tan(radians((90.0 - e) / 2.0))

def r_can(r_eq, e=axial_tilt):
    # radius of tropic of cancer, given the equator
    return r_eq * math.tan(radians((90.0 - e) / 2.0))

def almucantar(a, req, lat):
    aa, ll = radians(a), radians(lat)
    ra = req * math.cos(aa) / (math.sin(ll) + math.sin(aa))
    ya = req * math.cos(ll) / (math.sin(ll) + math.sin(aa))
    return ra, ya

#
#   Intersection of 2 circles.
#   
#   Assumes y==0 for both circles.

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

    return (xi, yi), (xii, yii)

#
#   Intersection of 2 circles

def intersect2(xy1, r1, xy2, r2):
    x1, y1 = xy1
    x2, y2 = xy2
    dx, dy = (x2 - x1), (y2 - y1)
    angle = math.atan2(dy, dx)
    dc = math.sqrt((dx * dx) + (dy * dy))

    c1 = Circle((x1, y1), r1)
    c2 = Circle((x2, y2), r2)
    p = Collection()
    p.add(c1)
    p.add(c2)
    # translate/rotate so circles lie on y==0 axis
    p.translate(-x1, -y1)
    p.rotate(-degrees(angle))

    inter = intersect(c1.x, c1.radius, c2.x, c2.radius)
    if inter is None: # no intersection
        return None

    (xi, yi), (xii, yii) = inter
    p = Polygon()
    p.add(xi, yi)
    p.add(xii, yii)
    # reverse the translate/rotate to restore the y axis component
    p.rotate(degrees(angle))
    p.translate(x1, y1)
    return p.points

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

def draw_almucantar(a, config, colour, work, rad_equator, outer):
    ra, ya = almucantar(a, rad_equator, config.latitude)
    circ = Circ(ya, ra)
    ii = outer.intersect(circ)
    if ii:
        (x0, y0), (x1, y1) = ii
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


def plate(drawing, config):
    s = config.size

    work = Collection()

    # equator and tropics
    rad_capricorn = s
    rad_equator = r_eq(rad_capricorn)
    rad_cancer = r_can(rad_equator)

    outer = Circ(0, rad_capricorn)
    c = outer.shape(colour=config.cut())
    work.add(c)

    circ = Circ(0, rad_equator)
    c = circ.shape(colour=config.thick_colour)
    work.add(c)

    circ = Circ(0, rad_cancer)
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
    for a in range(0, 90, config.almucantar):
        colour = config.thin_colour
        if (a % 10) == 0:
            colour = config.thick_colour
        draw_almucantar(a, config, colour, work, rad_equator, outer)

    # twilight arcs
    if config.twilight:
        colour = config.dotted_colour
        for twilight in config.twilight:
            draw_almucantar(twilight, config, colour, work, rad_equator, outer)

    # azimuth lines
    if 1:
        # horizon circle
        hr, hx = almucantar(0.0, rad_equator, config.latitude)
        # zenith / nadir
        yz =  rad_equator * math.tan(radians(90.0 - config.latitude) / 2.0)
        yn = -rad_equator * math.tan(radians(90.0 + config.latitude) / 2.0)
        # x centre for all circles
        yc = (yz + yn) / 2.0
        yaz = (yz - yn) / 2.0
        for angle in range(0, 90, config.azimuth):
            # calculate the azimuth circle x and radius
            xa = yaz * math.tan(radians(angle))
            ra = yaz / math.cos(radians(angle))

            def arc_angle(x, y):
                return 90.0 - degrees(math.atan2(x - yc, y - xa))

            # intersection with the horizon circle
            inter = intersect2((hx, 0), hr, (yc, xa), ra)
            assert inter, angle
            (x1, y1), (x2, y2) = inter
            # calculate the arc angles
            a1 = arc_angle(x1, y1)
            a2 = arc_angle(x2, y2)

            # intersection with the tropic of capricorn
            inter = intersect2((0, 0), rad_capricorn, (yc, xa), ra)
            assert inter, angle
            (x1, y1), (x2, y2) = inter
            # calculate the arc angle
            a3 = arc_angle(x2, y2)
            if a3 < a2:
                a2 = a3

            # add azimuth arc
            c = Arc((yc, xa), ra, a1, a2)
            work.add(c)
            # add same reflected in the x axis
            c = Arc((yc, xa), ra, a1, a2)
            c.reflect_h()
            work.add(c)

    work.draw(drawing, config.thick_colour)

#
#

def mater(drawing, config):
    work = Collection()
    inner = config.size * 1.01
    outer = config.size * 1.2
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
        t = Text((0, 0), "%0.1d" % label, height=config.size/35.0)
        t.rotate(-a)
        r = small - 1
        x, y = r * math.sin(rad), r * math.cos(rad)
        t.translate(x, y)
        t.rotate(-0.3)
        work.add(t)

        # hours
        t = Text((0, 0), hours[idx % 12], height=config.size/20.0)
        t.rotate(-a)
        r = mid - 2
        x, y = r * math.sin(rad), r * math.cos(rad)
        t.translate(x, y)
        t.rotate(-90 - 8)
        work.add(t)

    # throne
    if 0:
        throne_base = outer * 1.05
        throne_angle = 10
        throne_r = config.size / 8.0
        throne_hole = throne_r / 4
        p = Collection()
        c = Arc((0, 0), throne_base, -throne_angle, throne_angle)
        p.add(c)
        work.add(p)

        c = Circle((outer + throne_r, 0), throne_r)
        work.add(c)
        c = Circle((outer + throne_r, 0), throne_hole, colour=config.cut())
        work.add(c)

    # draw it all
    work.draw(drawing, config.thick_colour)

#
#

if __name__ == "__main__":
    drawing = dxf.drawing("test.dxf")
    config = Config()

    config.latitude = 50.37
    config.twilight = [ Twilight.nautical, Twilight.civil, Twilight.astronomical ]
    config.almucantar = 2
    config.azimuth = 15

    config.size = 100.0
    plate(drawing, config)

    mater(drawing, config)

    drawing.save()

# FIN
