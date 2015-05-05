#!/usr/bin/python

import math
import sys

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import Text, degrees

#
#

thick = 3

#
#

def make_lens(draw):
    h = 100
    r = 150
    t = 2
    work = Collection()
    c = Polygon()
    c.add(-t, 0)
    c.add(-t, h)
    work.add(c)
    m = h / 2.0
    d = math.sqrt((r * r) - (m * m))
    a = degrees(math.asin(m / r))
    c = Arc((-d, m), r, -a, a)
    work.add(c)

    r1 = 3 / 2.0
    r2 = 3.0
    def make_end():
        work = Collection()
        c = Circle((0, 0), r1)
        work.add(c)
        theta = degrees(math.asin(t / r2))
        c = Arc((0, 0), r2, 270 + theta, 270)
        work.add(c)
        d = math.sqrt((r2 * r2) - (t * t))
        c = Polygon()
        c.add(t, -r2)
        c.add(t, -d)
        work.add(c)
        return work

    c = make_end()
    c.translate(-t, h + r2)
    work.add(c)

    c = make_end()
    c.rotate(180)
    c.reflect_v()
    c.translate(-t, -r2)
    work.add(c)

    return work

#
#

x_margin = 10
y_margin = 20

def commit(work):
    #work.translate(x_margin, y_margin)
    work.draw(drawing, config.cut())

config = Config()

drawing = dxf.drawing("test.dxf")

draw = False

if len(sys.argv) > 1:
    draw = True

work = make_lens(draw)

commit(work)

drawing.save()

# FIN
