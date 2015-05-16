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

work = Collection()
r1 = Rectangle((0, 0), (w, h))
r2 = r1.copy()
r2.translate(20, 20)

p = ops.union(r1, r2)
work.add(p)

work.draw(drawing, config.cut())

drawing.save()

# FIN
