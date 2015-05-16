#!/usr/bin/python

import math

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import radians, rotate_2d, splice
from render import DXF as dxf

import ops

#
#

def curve(x0, y0, r, a0, a1, min_d=0.2):
    p = Polygon()
    circ = math.pi * r
    divs = circ / min_d
    div = 360.0 / divs
    angle = a0
    while angle < a1:
        x, y = rotate_2d(radians(angle), r, 0)
        p.add(x + x0, y + y0)
        angle += div
    return p

def curves(x0, y0, r0, r1, a0, a1):
    p = curve(x0, y0, r0, a0, a1)
    c = curve(x0, y0, r1, a0, a1)
    c.points.reverse()
    p.add_poly(c)
    return p

#
#

config = Config()

drawing = dxf.drawing("test.dxf")

w = 100 
h = 150
edge = 8
strip = 2
a_step = 5
step = 8
tab_len = 5
tab_d = 4

r = Rectangle((0, 0), (w*2, strip))

rects = []

for angle in range(0, 90, a_step):
    rr = r.copy()
    rr.rotate(angle)
    rects.append(rr)

for d in range(10, h, step):
    c = curves(edge, edge, d, d + strip, 0, 91)
    rects.append(c)

shape = ops.Shape(rects[0])

for r in rects[1:]:
    shape = shape.union(ops.Shape(r))

r = Rectangle((0, 0), (w, h))

# cut the tabs

for i in range(20, h, tab_len):
    print "not working yet ..."
    break
    p = Polygon()
    if (i % 2):
        x0, y0, x1, y1 = w, i, w + tab_d, i + tab_len
        continue
    else:
        x0, y0, x1, y1 = 0, i, -tab_d, i+tab_len

    p.add(x0, y1)
    p.add(x1, y1)
    p.add(x1, y0)
    p.add(x0, y0)

    if isinstance(r, Rectangle):
        r = Collection(r)

    r = splice(r, p)

shape = shape.intersection(ops.Shape(r))

#
r = Rectangle((edge, edge), (w-edge, h-edge))
s = ops.Shape(r)
r = Rectangle((0, 0), (w, h))


s = s.symmetric_difference(ops.Shape(r))
shape = shape.union(s)

work = shape.get()

work.draw(drawing, config.cut())

drawing.save()

# FIN
