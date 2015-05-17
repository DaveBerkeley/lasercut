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

def design():
    a_step = 5
    step = 8
    strip = 2

    rect = Rectangle((0, 0), (w*2, strip))

    rects = []

    for angle in range(0, 90, a_step):
        rr = rect.copy()
        rr.rotate(angle)
        rects.append(rr)

    diag = int(abs(complex(w, h)))
    for d in range(step * 3, int(diag), step):
        c = curves(edge, edge, d, d + strip, 0, 91)
        rects.append(c)

    shape = ops.Shape(rects[0])

    for r in rects[1:]:
        shape = shape.union(ops.Shape(r))

    e = edge / 2
    r = Rectangle((e, e), (w-e, h-e))
    shape = shape.intersection(ops.Shape(r))
    return shape

#
#

config = Config()

drawing = dxf.drawing("test.dxf")

w = 180 
h = 250
thick = 3
edge = 8
tabs = 10
tab_d = thick
#extra = 20
top = 10
bot = 10

shape = design()

#
r = Rectangle((edge, edge), (w-edge, h-edge))
s = ops.Shape(r)
r = Rectangle((0, -bot), (w, h+top))

s = s.symmetric_difference(ops.Shape(r))
shape = shape.union(s)

work = shape.get()
work.translate(0, bot)

# cut the tabs

if 1:
    tab_len = (h+top+bot)/tabs
    i, y = 0, 0
    while y < (h+top+bot):
        if (i % 2) == 0:
            x = 0
            dx = -thick
        else:
            x = w
            dx = thick
        p = Polygon((x, y + (tab_len/2)))
        p.add(x, y)
        p.add(x+dx, y)
        p.add(x+dx, y+tab_len)
        p.add(x, y+tab_len)
        work = splice(work, p)
        i += 1
        y += tab_len

work.draw(drawing, config.cut())

drawing.save()

# FIN
