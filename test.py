#!/usr/bin/python

import laser

# https://pypi.python.org/pypi/SDXF
import sdxf

# or use :
# https://pypi.python.org/pypi/dxfwrite/
# ?

#
#

kerf = 0.5
material = laser.Material(w=200, h=200, t=4)

config = laser.Config(kerf=kerf, material=material)

drawing = sdxf.Drawing()

drawing.saveas("test.dxf")

# FIN
