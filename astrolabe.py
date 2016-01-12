#!/usr/bin/python

import sys

from laser import Polygon, Circle, Collection, Config
from laser import radians, rotate_2d
from render import DXF as dxf

#
#

if __name__ == "__main__":

    r = 100

    config = Config()
    work = Collection()

    drawing = dxf.drawing("test.dxf")
    c = Circle((0, 0), r)
    work.add(c)
    work.draw(drawing, config.cut())

    drawing.save()

# FIN
