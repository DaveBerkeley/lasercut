#!/usr/bin/python

import sys
import math

from laser.render import DXF as dxf
from laser.laser import Config, Collection, Polygon, Circle, Rectangle, corner, radians

#
#

def edge(w, h, s, hole):
    work = Polygon()
    work.add(0, 0)
    work.add(w, 0)
    work.add(w, s)
    work.add(s, s)
    work.add(s, h-s)
    work.add(0, h-s)
    work.close()
    # add the bolt holes
    e = s / 2
    locs = [
        (e, e), (w-e, e),
    ]
    for x, y in locs:
        c = Circle((x, y), hole/2)
        work.add_arc(c)

    # add corners
    work = corner(work, (0, 0), e)
    work = corner(work, (w, 0), e)
    # inside
    work = corner(work, (s, s), e)

    return work

def end_plate(w, h, s, hole):
    work = Rectangle((0, 0), (w, h))
    e = s / 2
    locs = [
        (e, e), (e, h-e), (w-e, h-e), (w-e, e),
    ]
    for x, y in locs:
        c = Circle((x, y), hole/2)
        work.add_arc(c)

    work = corner(work, (0, 0), e)
    work = corner(work, (0, h), e)
    work = corner(work, (w, h), e)
    work = corner(work, (w, 0), e)

    return work

#
#

if __name__ == "__main__":

    single = False
    if len(sys.argv) >= 2:
        single = True

    config = Config()
    drawing = dxf.drawing()

    w = 40.0
    h = 50.0
    s = 6.0
    hole = 3.0
    spacing = 1.0

    if single:
        work = Collection()

        p = edge(w, h, s, hole)
        work.add(p)

        p = p.copy()
        p.rotate(180)
        p.translate(w, h)
        work.add(p)

        p = end_plate(w, h, s, hole)
        p.translate(w + spacing, 0)
        work.add(p)

        work.draw(drawing, config.cut())
    else:
        dx = abs(complex(s + spacing, s + spacing))
        for i in range(20):
            work = edge(w, h, s, hole)
            work.rotate(-45)
            work.translate(i * dx, 0)
            work.draw(drawing, config.cut())

        work = end_plate(h, w, s, hole)
        d = ((h - s) * math.sin(radians(45))) + spacing
        work.translate(0, d)
        lid = work.copy()
        # make a lid with a hole
        r = Rectangle((s, s), (h-s, w-s))
        r = corner(r, (s, s), s/2)
        r = corner(r, (h-s, w-s), s/2)
        r.translate(0, d)
        work.add(r)
        work.draw(drawing, config.cut())

        work = lid.copy()
        work.translate(h + spacing, 0)
        work.draw(drawing, config.cut())

        work.translate(h + spacing, 0)
        work.draw(drawing, config.cut())

        # add spacers
        work = Collection()
        p = Polygon()
        c = Circle((0, 0), s / 2)
        p.add_arc(c.copy())
        c = Circle((0, 0), hole / 2)
        p.add_arc(c.copy())

        work.add(p)
        work.translate((s/2) + (3 * (h + spacing)), (s/2) + d)

        for i in range(8):
            for j in range(6):
                w = work.copy()
                w.translate(i * (s + spacing), j * (s + spacing))
                w.draw(drawing, config.cut())

    drawing.save()

# FIN
