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

def make_gear(draw):
    work = Collection()
    c = Circle((0, 0), 7)
    work.add(c)
    c = Arc((0, 10), 7, 0, 180)
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

nteeth = 8
dia = 40

work = Collection()

for t in range(40):
    c = make_gear(draw)
    c.rotate(-90)
    c.translate(dia, 0)
    angle = t * 360.0 / nteeth
    c.rotate(angle)
    work.add(c)

    c = Polygon()
    c.add(0, dia * 0.8)
    c.add(0, dia)
    c.rotate(angle)
    work.add(c)

c = Circle((0, 0), dia)
work.add(c)
c = Circle((0, 0), dia * 0.8)
work.add(c)

commit(work)

drawing.save()

# FIN
