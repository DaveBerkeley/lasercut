#!/usr/bin/python

from laser import Rectangle, Config, Material, TCut

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#

kerf = 0.5
material = Material(w=200, h=200, t=4)

config = Config(kerf=kerf, material=material)

drawing = dxf.drawing("test.dxf")

shape = Rectangle(config, (0, 0), (20, 30), hole=False)
shape.draw(drawing, config.cut())

m4 = TCut(w=4, d=11, shank=6, nut_w=10, nut_t=3)

shape = m4.make_elev((0, 15), 90)
shape.draw(drawing, config.cut())

drawing.save()

# FIN
