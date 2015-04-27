#!/usr/bin/python

#!/usr/bin/python

from laser import Rectangle, Polygon, Config, Material, TCut, splice, cutout

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

class Collection:
    def __init__(self):
        self.data = []
    def add(self, obj):
        self.data.append(obj)
    def draw(self, drawing, colour):
        for data in self.data:
            data.draw(drawing, colour)

def hinge(work, xy0, xy1, on, off, pitch):
    c = Collection()
    c.add(work)

    y0, y1 = xy0[1], xy1[1]
    x0, x1 = xy0[0], xy1[0]
    for x in range(int(x0), int(x1), pitch*2):
        for y in range(int(y0), int(y1), int(on+off)):
            poly = Polygon()
            poly.add(x, y)
            poly.add(x, y+on)
            c.add(poly)
    for x in range(int(x0+pitch), int(x1), pitch*2):
        for y in range(int(y0+off), int(y1), int(on+off)):
            poly = Polygon()
            poly.add(x, y)
            poly.add(x, y+on)
            c.add(poly)

    return c

#
#

thick = 4
w = 100
h = 60

config = Config()

drawing = dxf.drawing("test.dxf")

work = Rectangle((0, 0), (w, h))

d = h/4.0
work = hinge(work, (w/4.0, 0), (3*w/4.0,h), d*0.8, d*0.2, 3)

work.draw(drawing, config.cut())

drawing.save()



# FIN
