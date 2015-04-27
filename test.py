#!/usr/bin/python

from laser import Rectangle, Polygon, Config, Material, TCut, splice, cutout

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

nut_x = 22

nut_locs = [
    [ nut_x, 0, 180 ],
    [ lout-nut_x, 0, 180 ],
    [ nut_x, win, 0 ],
    [ lout-nut_x, win, 0 ],
]

for x, y, rot in nut_locs:
    nut = m4.make_elev((x, y), rot)
    side = splice(side, nut)

cut_len = 8
cut_in = 7
template = cutout(thick, cut_len)

cut_locs = [
    [ cut_in, 0, 0 ],
    [ lout-cut_in, 0, 0 ],
    [ lout-cut_in, win, 180 ],
    [ cut_in, win, 180 ],
]

for x, y, rot in cut_locs:
    c = template.copy()
    c.rotate(rot)
    c.translate(x, y)
    side = splice(side, c)

side.draw(drawing, config.cut())

drawing.save()

# FIN
