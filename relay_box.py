#!/usr/bin/python

import sys

from laser.laser import Rectangle, Polygon, Circle, Collection, Config, Material
from laser.laser import TCut, Text, splice, cutout, corner
from laser.render import DXF as dxf

from laser.parts import mini_usb

#
#

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

thick = 3

config = Config()

drawing = dxf.drawing("test.dxf")

nut = TCut(w=3, d=12-thick, shank=5, nut_w=5.5, nut_t=2.3, stress_hole=0.25)

win = 43
end_space = 5
lin = 70 + end_space
hin = 25

nut_x = 24
nut_xa = 24 + 8
cut_len = 6
cut_in = 7
between_work = 1

tab_in = 14
tab_len = 6
foot_depth = 3

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

    work = corner(work, (0, 0), overhang)
    work = corner(work, (0, lid_w), overhang)
    work = corner(work, (lout, lid_w), overhang)
    work = corner(work, (lout, 0), overhang)

    prev = work.copy()
    move_margin(work)
    work.draw(drawing, config.cut())

#
#   Bottom plate

work = Collection()
work.add(prev)

usb_up = 10
usb_in = cut_in + (thick/2.0) + 6

class Relay:
    dy = 33
    dx = 44
    edge = 3
    hole = 3

relay = Relay()

# need fixing holes in bottom plate for relay board

relay_x = lout - cut_in - thick - relay.edge - relay.dx - end_space

c = Circle((0, 0), relay.hole/2.0)
d = c.copy()
d.translate(relay_x, (lid_w/2.0) - (relay.dy/2.0))
work.add(d)

d = c.copy()
d.translate(relay_x, (lid_w/2.0) + (relay.dy/2.0))
work.add(d)

work.translate(x_margin, y_margin + lid_w + between_work)
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

work = Collection(work)
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
    [ lout/2.0, 0, 180 ],
    [ tab_in, hin, 0 ],
    [ lout-tab_in, hin, 0 ],
    [ lout/2.0, hin, 0 ],
]

template = cutout(tab_len, thick)

work = add_cutouts(work, cut_locs, template)

# feet / tabs

cut_locs = [
    [ tab_in, 0, 180 ],
    [ lout-tab_in, 0, 180 ],
]

template = cutout(tab_len, thick + foot_depth)

work = add_cutouts(work, cut_locs, template)

prev = work.copy()

# flip it round so the feet stick upwards
work.rotate(180)
ex = work.extent()
# move so it sits on 0,0 point
work.translate(0, -ex.origin[1])
work.translate(-ex.origin[0], 0)

move_margin(work)
work.translate(lout + between_work, 0)
work.draw(drawing, config.cut())

#
# Other side plate

c = prev.copy()
work = Collection()
work.add(c)

c = mini_usb()
c.translate(usb_in, usb_up)
work.add(c)

move_margin(work)
work.translate(lout + between_work + tab_len + between_work, hin + (3 * thick) + between_work)
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

work = add_cutouts(Collection(work), cut_locs, template)

cut_locs = [
    [ end_w/2.0, 0, 180 ],
    [ end_w/2.0, hin, 0 ],
]

template = cutout(tab_len, thick)

work = add_cutouts(work, cut_locs, template)
prev = work.copy()

# Add text to this instance
c = work
work = Collection()
work.add(c)
# TODO : text positioning seems incorrect!
c = Text((-13, 14), "Relay V1.1", height=3.0, colour=Config.engrave_colour)
work.add(c)

work.rotate(90)
work.translate(hin + thick, 0)
work.translate(x_margin + lout + between_work + tab_len, y_margin + (hin * 2) + (thick*3) + (2 * between_work))
work.draw(drawing, config.cut())

#
#   Second end plate

if 1:
    c = prev.copy()
    work = Collection()
    work.add(c)

    # add the cable holes
    c = Circle((2*end_w/3.0, hin/2.0), cable_r)
    work.add(c)
    c = Circle((end_w/3.0, hin/2.0), cable_r)
    work.add(c)

    work.rotate(90)
    work.translate(hin + thick, 0)
    work.translate(x_margin + (2*lout)+ between_work + tab_len - hin - (2*thick), y_margin + (2 * between_work) + (hin*2) + (3 * thick))
    work.draw(drawing, config.cut())

#
#

drawing.save()

# FIN
