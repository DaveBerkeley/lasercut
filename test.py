#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Config, Material, TCut, splice, cutout

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

def add_cutouts(work, locs, template):
    for x, y, rot in locs:
        c = template.copy()
        c.rotate(rot)
        c.translate(x, y)
        work = splice(work, c)
    return work

def move_margin(work):
    work.translate(10, 20)

#
#

thick = 4
material = Material(w=200, h=200, t=thick)

config = Config(material=material)

drawing = dxf.drawing("test.dxf")

m4 = TCut(w=3, d=7, shank=3, nut_w=6, nut_t=2, stress_hole=0.25)

win = 39
lin = 75
hin = 21

nut_x = 24
cut_len = 6
cut_in = 7
between_work = 1

tab_in = 14
tab_len = 6

wout = win + (thick * 2)
lout = lin + (thick) + (2 * cut_in)

if 0:
    work = Rectangle((0, 0), (lout, wout))

    work.draw(drawing, config.cut())

    drawing.save()
    sys.exit()

#
#   Side plate

work = Rectangle((0, 0), (lout, hin))

nut_locs = [
    [ nut_x, 0, 180 ],
    [ lout-nut_x, 0, 180 ],
    [ nut_x, hin, 0 ],
    [ lout-nut_x, hin, 0 ],
]

for x, y, rot in nut_locs:
    nut = m4.make_elev((x, y), rot)
    work = splice(work, nut)

cut_locs = [
    [ cut_in, 0, 0 ],
    [ lout-cut_in, 0, 0 ],
    [ lout-cut_in, hin, 180 ],
    [ cut_in, hin, 180 ],
]

template = cutout(thick, cut_len)

work = add_cutouts(work, cut_locs, template)

cut_locs = [
    [ tab_in, 0, 180 ],
    [ lout-tab_in, 0, 180 ],
    [ lout/2.0, 0, 180 ],
    [ tab_in, hin, 0 ],
    [ lout-tab_in, hin, 0 ],
    [ lout/2.0, hin, 0 ],
]

template = cutout(tab_len, thick)

work = add_cutouts(work, cut_locs, template)

ex = work.extent()

move_margin(work)
work.draw(drawing, config.cut())

#

wdy = ex.corner[1] - ex.origin[1]
work.move(0, wdy + between_work)
move_margin(work)
work.draw(drawing, config.cut())

#

ex = work.extent()

end_w = win + thick + thick
work = Rectangle((0, 0), (end_w, hin))

cut_locs = [
    [ 0, hin/2.0, -90 ],
    [ end_w, hin/2.0, 90 ],
]

template = cutout(10, thick)

work = add_cutouts(work, cut_locs, template)

cut_locs = [
    [ end_w/2.0, 0, 180 ],
    [ end_w/2.0, hin, 0 ],
]

template = cutout(tab_len, thick)

work = add_cutouts(work, cut_locs, template)

wdy = ex.corner[1]
work.move(0, wdy + between_work)
work.translate(10, 0)
work.draw(drawing, config.cut())

#

ex = work.extent()
wdx = ex.corner[0] - ex.origin[0]
work.translate(wdx + between_work, 0)
work.draw(drawing, config.cut())

#
#

drawing.save()

# FIN
