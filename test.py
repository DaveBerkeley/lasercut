#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Circle, Collection, Config, Material
from laser import TCut, splice, cutout

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

if 1:
    overhang = 3
    lid_w = wout + (2 * overhang)
    work = Collection()
    c = Rectangle((0, 0), (lout, lid_w))
    work.add(c)

    to_side = (thick / 2.0) + overhang
    nut_locs = [
        [ nut_x, to_side, 0 ],
        [ lout-nut_x, to_side, 0 ],
        [ nut_x, lid_w-to_side, 0 ],
        [ lout-nut_x, lid_w-to_side, 0 ],
    ]

    for x, y, rot in nut_locs:
        c = m4.make_plan((x, y), rot);
        work.add(c)

    c_to_side = to_side # + (thick/2.0)
    slot_1 = Rectangle((-cut_len/2.0, -thick/2.0), (cut_len/2.0, thick/2.0))
    slot_2 = Rectangle((-thick/2.0, -tab_len/2.0), (thick/2.0, tab_len/2.0))
    cut_locs = [
        [ tab_in, c_to_side, slot_1 ],
        [ lout-tab_in, c_to_side, slot_1 ],
        [ tab_in, lid_w-c_to_side, slot_1 ],
        [ lout-tab_in, lid_w-c_to_side, slot_1 ],
        [ lout/2.0, c_to_side, slot_1 ],
        [ lout/2.0, lid_w-c_to_side, slot_1 ],

        [ cut_in, lid_w/2.0, slot_2 ],
        [ lout-cut_in, lid_w/2.0, slot_2 ],
    ]

    for x, y, slot in cut_locs:
        c = slot.copy()
        c.rotate(rot)
        c.translate(x, y)
        work.add(c)

    #work.rotate(30)
    move_margin(work)
    work.draw(drawing, config.cut())

    #drawing.save()

#
#   Bottom plate

work.translate(0, lid_w + between_work)
work.draw(drawing, config.cut())

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

# move so it sits on 0 y-axis
ex = work.extent()
work.translate(0, -ex.origin[1])

move_margin(work)
work.translate(lout + between_work, 0)
work.draw(drawing, config.cut())

#
# Other side plate

work.translate(0, hin + (2 * thick) + between_work)
work.draw(drawing, config.cut())

#
#   End plate

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
work.translate(10 + lout + between_work, 0)
work.draw(drawing, config.cut())

#
#   Second side plate

work.translate(end_w + between_work, 0)
work.draw(drawing, config.cut())

#
#

drawing.save()

# FIN
