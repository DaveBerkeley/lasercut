#!/usr/bin/python

from laser import Rectangle, Polygon, Config, Material, Collection, Text, hinge

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#

x_margin = 10
y_margin = 20
spacing = 1

thick = 4
w = 100
h = 40

config = Config()

drawing = dxf.drawing("test.dxf")

for i, pitch in enumerate( [ 1.0, 1.5, 2.0, 2.5, 3.0 ] ):
    work = Rectangle((0, 0), (w, h))

    d = h/4.0
    work = hinge(work, (w/4.0, 0), (3*w/4.0,h), d*0.8, d*0.2, pitch)

    r = Text((2, 10), "pitch %.1f" % pitch, height=3.0)
    work.add(r)

    work.translate(0, i * (h + spacing))
    work.translate(x_margin, y_margin)
    work.draw(drawing, config.cut())

drawing.save()



# FIN
