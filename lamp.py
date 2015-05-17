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

def x_design():

    step = 20
    strip = 2
    shape = None
    e = edge / 2
    for x in range(e, w-e, 20):
        r = Rectangle((x, e), (x+strip, h-e))
        if shape is None:
            shape = ops.Shape(r)
        else:
            shape = shape.union(ops.Shape(r))
    for y in range(e, h-e, 20):
        r = Rectangle((e, y), (w-e, y+strip))
        shape = shape.union(ops.Shape(r))

    return shape

def band(x, y, r, strip):
    c = Circle((x, y), r)
    shape = ops.Shape(c)
    c = Circle((x, y), r+strip)
    shape = shape.symmetric_difference(ops.Shape(c))
    return shape

def design():
    strip = 2

    def pool(x, y):
        shape = None
        for r in range(80, 80, 10):
            c = band(x, y, r, strip)
            if shape:
                shape = shape.union(c)
                break
            else:
                shape = c
        return shape

    xy = [
        (50, 50), (100, 100), (45, 120),
    ]
    shape = None
    for x, y in xy:
        for r in range(50, 10, -10):
            r = band(x, y, r, strip)
            if shape:
                shape = shape.union(r)
            else:
                shape = r
    return shape

def xdesign():

    def star(x0, y0, d):
        n = 5
        p = Polygon()
        for angle in range(0, 360, 360/n):
            print angle
            x, y = rotate_2d(radians(angle), 0, d)
            p.add(x, y)
            angle += 180/n
            x, y = rotate_2d(radians(angle), 0, 2.0 * d / 5.0)
            p.add(x, y)
        p.close()
        p.translate(x0, y0)
        return p

    def make(x0, y0, d):
        s = star(x0, y0, d)
        shape = ops.Shape(s)
        s = star(x0, y0, d-5)
        shape = shape.symmetric_difference(ops.Shape(s))
        return shape

    shape = make(50, 50, 80)
    s = make(150, 150, 80)
    shape = shape.union(s)
    s = make(100, 80, 50)
    shape = shape.union(s)
    return shape

def design():

    shape = None
    for x in range(10, w, 18):
        for y in range(10, h, 18):
            s = band(x, y, 14, 2)
            if shape:
                shape = shape.union(s)
            else:
                shape = s
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
top = 10
bot = 50


shape = design()

# clip the design
e = edge/2
r = Rectangle((e, e), (w-e, h-e))
shape = shape.intersection(ops.Shape(r))

# frame the design

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
