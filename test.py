#!/usr/bin/python

from laser import Rectangle, Config, Material, TCut, splice

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#

kerf = 0.5
material = Material(w=200, h=200, t=4)

config = Config(kerf=kerf, material=material)

drawing = dxf.drawing("test.dxf")

shape = Rectangle(config, (0, 0), (50, 30))

m4 = TCut(w=4, d=11, shank=6, nut_w=10, nut_t=3)

item = m4.make_elev((0, 15), 90)
shape = splice(shape, item)

item = m4.make_elev((50, 15), -90)
shape = splice(shape, item)

item = m4.make_elev((25, 0), -180)
shape = splice(shape, item)

#shape.rotate(30)

shape.draw(drawing, config.cut())

drawing.save()

# FIN
