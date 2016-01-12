#!/usr/bin/python

import sys
import math

from laser import Circle, Collection, Config
from laser import radians
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

class Circ:

    def __init__(self, x, r):
        self.x = x
        self.r = r

    def shape(self, s):
        return Circle((self.x * s, 0), self.r * s)

#
#

if __name__ == "__main__":

    s = 100

    config = Config()
    work = Collection()

    drawing = dxf.drawing("test.dxf")

    for a in range(0, 91, 5):
        m, r = project(a)
        print a, m, r
        cc = Circ(m, r)
        c = cc.shape(s)
        work.add(c)

    cc = Circ(0, 1)
    c = cc.shape(s)
    work.add(c)

    work.draw(drawing, config.cut())

    drawing.save()

# FIN
