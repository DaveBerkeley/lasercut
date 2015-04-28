#!/usr/bin/python

#!/usr/bin/python

from laser import Rectangle, Polygon, Config, Material, Collection, hinge

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

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

#work.move(5, 5)
#work.rotate(90)

work.draw(drawing, config.cut())

drawing.save()



# FIN
