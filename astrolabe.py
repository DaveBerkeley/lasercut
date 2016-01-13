#!/usr/bin/python

import sys
import math

from laser import Arc, Circle, Collection, Config
from laser import radians, degrees
from render import DXF as dxf

#
#

axial_tilt = 23.4
latitude = 52.0

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

    def shape(self, s):
        return Circle((self.x * s, 0), self.r * s)

    def intersect(self, c):
        return intersect(self.x, self.r, c.x, c.r)


#
#

if __name__ == "__main__":

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
            #c = Circle((s* x0, s * y0), s * 0.05)
            #work.add(c)
            #c = Circle((s* x1, s * y1), s * 0.05)
            #work.add(c)

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

    work.draw(drawing, config.cut())

    drawing.save()

# FIN
