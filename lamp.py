#!/usr/bin/python

import math

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import radians, rotate_2d, splice
from render import DXF as dxf

import ops

#
#

def curve(x0, y0, r, a0, a1, min_d=0.2):
    arc = Arc((x0, y0), r, a0, a1)
    return ops.arc_to_poly(arc)

def curves(x0, y0, r0, r1, a0, a1):
    p = curve(x0, y0, r0, a0, a1)
    c = curve(x0, y0, r1, a0, a1)
    c.points.reverse()
    p.add_poly(c)
    p.close()
    return p

#
#

config = Config()

drawing = dxf.drawing("test.dxf")

w = 180 
h = 250
thick = 3
edge = 8
strip = 2
a_step = 5
step = 8
tab_len = 5
tab_d = thick

r = Rectangle((0, 0), (w*2, strip))

rects = []

for angle in range(0, 90, a_step):
    rr = r.copy()
    rr.rotate(angle)
    rects.append(rr)

diag = int(abs(complex(w, h)))
for d in range(step * 3, int(diag), step):
    c = curves(edge, edge, d, d + strip, 0, 91)
    rects.append(c)

shape = ops.Shape(rects[0])

for r in rects[1:]:
    shape = shape.union(ops.Shape(r))

r = Rectangle((0, 0), (w, h))
shape = shape.intersection(ops.Shape(r))

# cut the tabs

for i in range(0, h, tab_len):
    if (i % 2):
        x0, y0, x1, y1 = w, i, w + tab_d, i + tab_len
    else:
        x0, y0, x1, y1 = 0, i, -tab_d, i+tab_len

    r = Rectangle((x0, y0), (x1, y1))
    shape = shape.union(ops.Shape(r))

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
