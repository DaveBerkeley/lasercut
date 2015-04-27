#!/usr/bin/python

import math

# http://pypi.python.org/pypi/SDXF
import sdxf

#
#

def bracket(x, y, s, w, angle):

    angle = 180 - angle

    angle = math.radians(angle)
    corners = [ (x, y), (x+s, y), (x + s*math.cos(angle), y + s*math.sin(angle)), ]
    points = corners[:] + [ (x, y) ]
    line = sdxf.PolyLine(points, color=4)
    drawing.append(line)

    # mid point between the far corners
    mx = (corners[1][0] + corners[2][0]) / 2
    my = (corners[1][1] + corners[2][1]) / 2

    points = [ (x, y), (mx, my) ]
    line = sdxf.PolyLine(points, color=6)
    drawing.append(line)

#
#

if __name__ == "__main__":

    size = 240.0
    support_width = 10
    angle = 60

    drawing = sdxf.Drawing()

    bracket(0, 0, size / 2, support_width, angle)

    drawing.saveas('angles.dxf')

# FIN
