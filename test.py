#!/usr/bin/python

from laser import Rectangle, Config, Material, TCut, splice

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#

thick = 4
material = Material(w=200, h=200, t=thick)

config = Config(material=material)

drawing = dxf.drawing("test.dxf")

m4 = TCut(w=4, d=11, shank=6, nut_w=10, nut_t=3, stress_hole=0.25)

win = 39
lin = 75
hin = 21
margin = (thick * 2) + 2
wout = win + margin
lout = lin + margin

side = Rectangle(config, (0, 0), (lout, win))

nut_x = 15

nut = m4.make_elev((nut_x, 0), 180)
side = splice(side, nut)

nut = m4.make_elev((lout - nut_x, 0), 180)
side = splice(side, nut)

#nut = m4.make_elev((nut_x, win), 0)
#side = splice(side, nut)

#nut = m4.make_elev((lout - nut_x, win), 0)
#side = splice(side, nut)

side.draw(drawing, config.cut())

drawing.save()

# FIN
