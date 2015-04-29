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

x_margin = 10
y_margin = 20

def move_margin(work):
    work.translate(x_margin, y_margin)

#
#

thick = 4
material = Material(w=200, h=200, t=thick)

config = Config(material=material)

drawing = dxf.drawing("test.dxf")

nut = TCut(w=3, d=12-thick, shank=3, nut_w=5.5, nut_t=2.3, stress_hole=0.25)

win = 43 + thick
lin = 75
hin = 25

nut_x = 24
nut_xa = 24 + 8
cut_len = 6
cut_in = 7
between_work = 1

tab_in = 14
tab_len = 6

wout = win + (thick * 2)
lout = lin + (thick) + (2 * cut_in)

cable_r = 7/2.0

if 1:
    overhang = 3
    lid_w = wout + (2 * overhang)
    work = Collection()
    c = Rectangle((0, 0), (lout, lid_w))
    work.add(c)

    to_side = (thick / 2.0) + overhang
    nut_locs = [
        [ nut_xa, to_side, 0 ],
        [ lout-nut_x, to_side, 0 ],
        [ nut_xa, lid_w-to_side, 0 ],
        [ lout-nut_x, lid_w-to_side, 0 ],
    ]

    for x, y, rot in nut_locs:
        c = nut.make_plan((x, y), rot);
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
    [ nut_xa, 0, 180 ],
    [ lout-nut_x, 0, 180 ],
    [ nut_xa, hin, 0 ],
    [ lout-nut_x, hin, 0 ],
]

for x, y, rot in nut_locs:
    c = nut.make_elev((x, y), rot)
    work = splice(work, c)

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
prev = work.copy()
ex = work.extent()
work.translate(0, -ex.origin[1])

move_margin(work)
work.translate(lout + between_work, 0)
work.draw(drawing, config.cut())

#
# Other side plate

c = prev.copy()
work = Collection()
work.add(c)

# TODO add USB socket

def mini_usb():
    usb_w1 = 7.7
    usb_w2 = 6.5
    usb_h = 3.95
    c = Polygon((0, 0))
    indent = (usb_w1 - usb_w2) / 2.0
    c.add(0, usb_h)
    c.add(usb_w1, usb_h)
    c.add(usb_w1, 2*usb_h/3.0)
    c.add(usb_w2 + indent, usb_h/3.0)
    c.add(usb_w2 + indent, 0)
    c.add(indent, 0)
    c.add(indent, usb_h/3.0)
    c.add(0, 2*usb_h/3.0)
    c.close()
    return c

usb_up = 10
usb_in = cut_in + (thick/2.0) + 6

c = mini_usb()
c.translate(usb_in, usb_up)
work.add(c)

move_margin(work)
work.translate(lout + between_work, hin + (3 * thick) + between_work)
work.draw(drawing, config.cut())

#
#   End plate

end_w = win + thick + thick
work = Rectangle((0, 0), (end_w, hin))

cut_locs = [
    [ 0, hin/2.0, -90 ],
    [ end_w, hin/2.0, 90 ],
]

s_cut = hin - (2 * cut_len)
template = cutout(s_cut, thick)

work = add_cutouts(work, cut_locs, template)

cut_locs = [
    [ end_w/2.0, 0, 180 ],
    [ end_w/2.0, hin, 0 ],
]

template = cutout(tab_len, thick)

work = add_cutouts(work, cut_locs, template)
prev = work.copy()

work.translate(x_margin + lout + between_work, y_margin + (hin * 2) + (thick*4) + (2 * between_work))
work.draw(drawing, config.cut())

#
#   Second end plate

c = prev.copy()
work = Collection()
work.add(c)

# add the cable holes
c = Circle((2*end_w/3.0, hin/2.0), cable_r)
work.add(c)
c = Circle((end_w/3.0, hin/2.0), cable_r)
work.add(c)

work.translate(x_margin + lout + between_work, y_margin + (3 * between_work) + (hin*3) + (6 * thick))
work.draw(drawing, config.cut())

#
#

drawing.save()

# FIN
