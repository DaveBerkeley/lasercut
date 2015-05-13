#!/usr/bin/python

from render import DXF as dxf
from parts import mini_usb
from laser import Config, Collection, corner

#
#

# TODO : move to parts.py
class ArduinoNano():

    def make_plan(self, draw=False):
        p = Collection()
        return p

    def make_elev(self, draw=False):
        usb = mini_usb()
        x, y = usb.centre()
        usb.translate(-x, 0)
        return usb

#
#

if __name__ == "__main__":
    config = Config()
    drawing = dxf.drawing()

    nano = ArduinoNano()
    work = nano.make_elev(True)

    if 0:
        corners = [ 0, 1, 4, 5, ]
        points = work.points[:]
        for i in corners:
            work = corner(work, points[i], 0.4, inside=True)

    work.draw(drawing, config.cut())
    
    drawing.save()

# FIN
