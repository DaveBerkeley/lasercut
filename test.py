#!/usr/bin/python

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

#
#

thick = 4
material = Material(w=200, h=200, t=thick)

config = Config(material=material)

drawing = dxf.drawing("test.dxf")

m4 = TCut(w=3, d=7, shank=3, nut_w=5, nut_t=2, stress_hole=0.25)

win = 39
lin = 75
hin = 21
margin = (thick * 2) + 2
wout = win + margin
lout = lin + margin

nut_x = 22
cut_len = 6
cut_in = 7
between_work = 1

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

work.draw(drawing, config.cut())

x, x, x, maxy = work.extent()
work.move(0, maxy + between_work)
work.draw(drawing, config.cut())

x, x, x, maxy = work.extent()

end_w = win + thick + thick
work = Rectangle((0, 0), (end_w, hin))

cut_locs = [
    [ 0, hin/2.0, -90 ],
    [ end_w, hin/2.0, 90 ],
]

template = cutout(10, thick)

work = add_cutouts(work, cut_locs, template)

work.move(0, maxy + between_work)

work.draw(drawing, config.cut())

x, x, x, maxy = work.extent()
work.move(0, maxy + between_work)

work.draw(drawing, config.cut())

drawing.save()

# FIN
