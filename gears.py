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

nteeth = 20
r1 = 100
angle = 2.86

v = Polygon()
v.add(0, 0)

for i in range(15):
    x, y = i * r1 / 20.0, r1
    x, y = rotate_2d(radians(i * angle), x, y)
    v.add(x, y)

for i in range(nteeth):

    c = v.copy()
    a = 360 / nteeth
    c.rotate(a * i)
    work.add(c)

    #c = v.copy()
    #c.reflect_v()
    #c.rotate(a * (i + 0.75))
    #work.add(c)

#work.add(v)
#c = v.copy()
#c.rotate(18)
#work.add(c)

#c = Circle((0, 0), r1)
#work.add(c)
commit(work)

drawing.save()

# FIN
