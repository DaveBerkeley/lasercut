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

#shape = Rectangle(config, (0, 0), (20, 30), hole=False)
#shape.draw(drawing, config.cut())

tcut = TCut(w=4, d=11, shank=6, nut_w=10, nut_t=3)
shape = tcut.make_elev((0, 0), 30)
shape.draw(drawing, config.cut())

drawing.save()

# FIN
