#!/usr/bin/python

import sys

from laser.laser import Polygon, Circle, Collection, Config
from laser.laser import radians, rotate_2d
from laser.render import DXF as dxf

from laser.gears import make_involute
from laser.kerf import dekerf

#
#

if __name__ == "__main__":
    x_margin = 10
    y_margin = 20

    draw = False

    if len(sys.argv) > 1:
        draw = True

    def commit(work):
        work.translate(x_margin, y_margin)
        work.draw(drawing, config.cut())

    config = Config()

    drawing = dxf.drawing("test.dxf")

    N = 20
    PA = 14.5
    pitch_dia = 20.0
    pr = pitch_dia / 2.0

    r = 1.5
    kerf = 0.2

    m = pitch_dia / N

    x, y = 0, 0
    for i, N in enumerate(range(10, 21, 1)):
        pd = m * N
        print(pd, N, "kerf=", kerf)
        work = make_involute(pd, N, PA)
        work = dekerf(work, kerf, False)
        x += work.info["outside_dia"]
        if x > 100:
            x = 0
            y +=  work.info["outside_dia"]

        c = Circle((0, 0), r)
        work.add_arc(c)
        d, mr = 3, 0.5
        c = Circle((0, d), mr)
        work.add_arc(c)
        c = Circle((0, -d), mr)
        work.add_arc(c)
        c = Circle((d, 0), mr)
        work.add_arc(c)
        c = Circle((-d, 0), mr)
        work.add_arc(c)
        work.translate(x + pr, y + pr)
        commit(work)

    drawing.save()

# FIN
