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

P = 16.0
N = 20
PA = 14.5

D = N / P
R = D / 2.0
DB = D * math.cos(radians(PA))
RB = DB / 2.0
a = 1.0 / P
d = 1.157 / P
DO = D + (2 * a)
RO = DO / 2.0
DR = D - (2 * d)
RR = DR / 2.0

CB = math.pi * DB
fcb = RB / 20.0
ncb = CB / fcb
acb = 360 / ncb
gt = 360.0 / N

print D, R, DB, RB
print a, d
print DO, RO, DR, RR
print CB,
print fcb, ncb, acb, gt

def scale(a):
    return a * 254

v = Polygon()
v.add(0, scale(RR))

# note : the range 5 .. 12 approximates to the intersection
# with the D and DO circles
for i in range(5, 12):
    x, y = i * RB / 20.0, RB
    x, y = [ scale(z) for z in [ x, y ] ]
    x, y = rotate_2d(radians(i * acb), x, y)
    v.add(x, y)

v.rotate(-gt / 4.0)
c = Collection()
c.add(v.copy())
v.reflect_v()
c.add(v.copy())
v = c

for i in range(N):
    c = v.copy()
    c.rotate(gt * i)
    work.add(c)

for r in [ R, RO, RR, RB ]:
    print r
    c = Circle((0, 0), scale(r))
    work.add(c)

commit(work)

drawing.save()

# FIN
