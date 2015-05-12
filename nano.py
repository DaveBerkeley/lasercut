#!/usr/bin/python

from render import DXF as dxf
from parts import mini_usb
from laser import Config, Collection

#
#

# TODO : move to parts.py
class ArduinoNano():

    def make_plan(self, draw=False):
        p = Collection()
        return p

    def make_elev(self, draw=False):
        work = Collection()
        usb = mini_usb()
        x, y = usb.centre()
        print x, y
        usb.translate(-x, 0)
        work.add(usb)
        return work

#
#

if __name__ == "__main__":
    config = Config()
    drawing = dxf.drawing()

    nano = ArduinoNano()
    work = nano.make_elev(True)

    work.draw(drawing, config.cut())
    
    drawing.save()

# FIN
