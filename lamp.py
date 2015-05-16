#!/usr/bin/python

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from render import DXF as dxf

import ops

#
#

config = Config()

drawing = dxf.drawing("test.dxf")

w = 100 
h = 150
edge = 8
strip = 3
step = 10

r = Rectangle((0, 0), (w*2, strip))

rects = []

angle = 30
for y in range(0, 200, step):
    rr = r.copy()
    rr.rotate(angle)
    #rr.translate(0, y)
    rects.append(rr)
    angle += 5

for y in range(0, 200, step):
    rr = r.copy()
    rr.rotate(-30)
    rr.translate(0, y)
    rects.append(rr)

shape = ops.Shape(rects[0])

for r in rects[1:]:
    print r
    shape = shape.union(ops.Shape(r))

r = Rectangle((0, 0), (w, h))
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
