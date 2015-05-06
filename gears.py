#!/usr/bin/python

import math
import sys

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import Text, degrees, radians, rotate_2d

#
#

thick = 3

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

work = Collection()

# Involute gears, see :
# http://www.cartertools.com/involute.html

r1 = 100
angle = 2.86

for i in range(15):
    p = Polygon()
    p.add(0, 0)
    p.add(0, r1)
    p.add(i * r1 / 20.0, r1)
    p.rotate(i * angle)
    work.add(p)

    #x, y = i * r1 / 20.0, r1
    #x, y = rotate_2d(radians(i * angle), x, y)
    #c = Circle((x, y), 10)
    #work.add(c)

c = Circle((0, 0), r1)
work.add(c)
commit(work)

drawing.save()

# FIN
