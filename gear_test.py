#!/usr/bin/python

import sys

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Polygon, Circle, Collection, Config
from laser import radians, rotate_2d

from gears import make_involute

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
    pitch_dia = 20
    pr = pitch_dia / 2.0

    r = 1.5

    x, y = 0, 0
    for i, N in enumerate(range(10, 20, 1)):
        work = make_involute(pitch_dia, N, PA)
        c = Circle((0, 0), r)
        work.add(c)
        work.translate(x + pr, y + pr)
        x += work.info["outside_dia"]
        if x > 100:
            x = 0
            y +=  work.info["outside_dia"]
        commit(work)

    drawing.save()

# FIN
