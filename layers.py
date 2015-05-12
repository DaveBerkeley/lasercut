#!/usr/bin/python

from render import DXF as dxf
from laser import Config, Collection, Polygon, Circle

#
#

def edge():
    work = Polygon()
    work.add(0, 0)
    work.add(w, 0)
    work.add(w, s)
    work.add(s, s)
    work.add(s, h-s)
    work.add(0, h-s)
    work.close()
    c = Circle((s/2, s/2), hole/2)
    work.add_arc(c)
    c = Circle((w-(s/2), s/2), hole/2)
    work.add_arc(c)
    return work

#
#

if __name__ == "__main__":
    config = Config()
    drawing = dxf.drawing()

    w = 40.0
    h = 50.0
    s = 6.0
    hole = 3.0

    if 0:
        work = Collection()

        p = edge()
        work.add(p)

        p = edge()
        p.rotate(180)
        p.translate(w, h)
        work.add(p)

        work.draw(drawing, config.cut())
    else:
        spacing = 1.0
        dx = abs(complex(s + spacing, s + spacing))
        for i in range(20):
            work = edge()
            work.rotate(-45)
            work.translate(i * dx, 0)
            work.draw(drawing, config.cut())
        
    drawing.save()

# FIN
