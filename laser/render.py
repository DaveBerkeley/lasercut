#
#

import math

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from .laser import radians, distance

#
#

class Render:
    pass

#
#

class DXF(Render):

    def __init__(self, filename="test.dxf"):
        self.drawing = dxf.drawing(filename)

    def save(self):
        self.drawing.save()

    def add(self, item):
        self.drawing.add(item)

    def circle(self, radius=None, center=None, color=None):
        item = dxf.circle(radius=radius, center=center, color=color)
        self.add(item)

    def arc(self, radius=None, center=None, startangle=None, endangle=None, color=None):
        item = dxf.arc(radius=radius, center=center, startangle=startangle, endangle=endangle, color=color)
        self.add(item)

    def line(self, xy0, xy1, color=None):
        item = dxf.line(xy0, xy1, color=color)
        self.add(item)

    def text(self, text, insert=None, rotation=0, color=None, **kwargs):
        item = dxf.mtext(text, insert=insert, rotation=rotation, color=color, **kwargs)
        self.add(item)

    @staticmethod
    def drawing(*args):
        return DXF(*args)

#
#

class Plot:
    def __init__(self):
        self.data = []
    def append(self, **kwargs):
        self.data.append(kwargs)

class GCODE:

    def __init__(self, filename="test.ngc"):
        self.plot = {}
        self.x = None
        self.y = None
        self.z = None
        self.d = {
            # TODO : these should be passed as tool / machine info
            'fast' : 300,
            'cut' : 50,
            'feedup' : 300,
            'feeddown' : 50,
            # heights
            'up' : 3,
            'down' : -1,
        }
        self.out = open(filename, "w")

    def write(self, text):
        self.out.write(text + "\n")

    def up(self):
        if self.z != self.d['up']:
            self.write("G00 Z%(up)s F%(feedup)s" % self.d)
            self.z = self.d['up']

    def down(self):
        if self.z != self.d['down']:
            self.write("G01 Z%(down)s F%(feeddown)s" % self.d)
            self.z = self.d['down']

    def setxy(self, x, y):
        self.x = x
        self.y = y

    def goto(self, x, y):
        if (self.x == x) and (self.y == y):
            return

        self.up()
        self.write("G00 X%.4f Y%.4f F%.4f" % (x, y, self.d['fast']))
        self.down()
        self.setxy(x, y)

    def plot_line(self, line):
        x0, y0 = line['start']
        x1, y1 = line['end']

        # start at the nearest end
        d0 = distance((self.x, self.y), (x0, y0))
        d1 = distance((self.x, self.y), (x1, y1))
        if d1 < d0:
            x0, y0, x1, y1 = x1, y1, x0, y0

        self.goto(x0, y0)
        self.write("G01 X%.4f Y%.4f F%.4f" % (x1, y1, self.d['cut']))
        self.setxy(x1, y1)

    def plot_circle(self, line):
        radius = line['radius']
        xc, yc = line['center']
        x0, y0 = xc - radius, yc
        self.goto(x0, y0)
        self.write("G02 I%.4f F%.4f" % (radius, self.d['cut']))
        self.setxy(x0, y0)

    def plot_arc(self, line):
        radius = line['radius']
        xc, yc = line['center']
        endangle = line['endangle']
        startangle = line['startangle']

        xx0 = radius * math.cos(radians(startangle))
        yy0 = radius * math.sin(radians(startangle))
        xx1 = radius * math.cos(radians(endangle))
        yy1 = radius * math.sin(radians(endangle))
        x0 = xc + xx0
        y0 = yc + yy0
        x1 = xc + xx1
        y1 = yc + yy1
        i = -xx0
        j = -yy0

        # start at the nearest end
        if self.x and self.y:
            d0 = distance((self.x, self.y), (x0, y0))
            d1 = distance((self.x, self.y), (x1, y1))
            if d1 < d0:
                d = {
                    'radius' : radius, 
                    'center' : (xc,yc), 
                    'endangle' : startangle, 
                    'startangle' : endangle, 
                    'reverse' : True,
                }
                return self.plot_arc(d)

        self.goto(x0, y0)

        if line.get('reverse'):
            self.write("G02 I%.4f J%.4f X%.4f Y%.4f F%.4f" % (i, j, x1, y1, self.d['cut']))
        else:
            self.write("G03 I%.4f J%.4f X%.4f Y%.4f F%.4f" % (i, j, x1, y1, self.d['cut']))

        self.setxy(x1, y1)

    def save(self):

        header = [
            # junk I copied from the emulator
            # FIX THIS
            "(G90 distance mode, G94 feed rate mode, G17 xy plane, G69 Turn off coordinate system rotation )",
            "G90 G94 G17 G69",
            "(G21 metric )",
            "G21",
            "(G53 goto position)",
            "G53 G0 Z0",
            "(T1 select tool 1, M6 tool change)",
            "T1 M6",
            #"()",
            #"S7640 M3",
            "(G54 select co-ordinate system 1)",
            "G54",
            "(M8 turn flood coolant on)",
            "M8",
            #"G0 X4.4764 Y2.9321",
            "(G43 tool length offset Z<offset> H<tool>)",
            "G43 Z1.4 H1",
            #"(T3 select tool 3)",
            #"T3",
        ]

        tail = [
            # TODO : home, turn stuff off
            "(M5 stop spindle)",
            "M5",
            "(M9 turn flood coolant off)",
            "M9",
            "(G53 goto position)",
            "G53 G0 Z0.",
            "(M30 end of program)",
            "M30",
        ]

        for line in header:
            self.write(line)

        for color, plot in list(self.plot.items()):
            #print color
            for line in plot.data:
                if line['fn'] == "line":
                    self.plot_line(line)
                if line['fn'] == "circle":
                    self.plot_circle(line)
                if line['fn'] == "arc":
                    self.plot_arc(line)

        for line in tail:
            self.write(line)

    def get_plot(self, color):
        if not color in self.plot:
            plot = Plot()
            self.plot[color] = plot
        return self.plot[color]

    def circle(self, radius=None, center=None, color=None):
        #print "circle", radius, center, color
        plot = self.get_plot(color)
        plot.append(fn="circle", radius=radius, center=center)

    def arc(self, radius=None, center=None, startangle=None, endangle=None, color=None):
        #print "arc", radius, center, startangle, endangle, color
        plot = self.get_plot(color)
        plot.append(fn="arc", radius=radius, center=center, startangle=startangle, endangle=endangle)

    def line(self, xy0, xy1, color=None):
        #print "line", xy0, xy1, color
        plot = self.get_plot(color)
        plot.append(fn="line", start=xy0, end=xy1)

    def text(self, text, insert=None, rotation=0, color=None, **kwargs):
        #print "text", text, insert, rotation, color, kwargs
        plot = self.get_plot(color)
        plot.append(fn="text", insert=insert, rotation=rotation)

    @staticmethod
    def drawing(*args):
        return GCODE(*args)

# FIN
