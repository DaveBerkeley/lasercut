#
#

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

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

    def __init__(self, filename="test.mgc"):
        self.plot = {}
        self.x = None
        self.y = None
        self.z = None
        self.d = {
            'fast' : 300,
            'cut' : 50,
            'feedup' : 100,
            'up' : 3,
            'feeddown' : 50,
            'down' : -1,
        }

    def up(self):
        if self.z != self.d['up']:
            print "G01 Z%(up)s F%(feedup)s" % self.d
            self.z = self.d['up']

    def down(self):
        if self.z != self.d['down']:
            print "G01 Z%(down)s F%(feeddown)s" % self.d
            self.z = self.d['down']

    def save(self):
        for color, plot in self.plot.items():
            #print color
            for line in plot.data:
                if line['fn'] != "line":
                    continue
                x0, y0 = line['start']
                x1, y1 = line['end']

                if (x0 != self.x) or (y0 != self.y):
                    self.up()
                    print "G00 X%s Y%s F%s" % (x0, y0, self.d['fast'])
                    self.down()
                print "G01 X%s Y%s F%s" % (x1, y1, self.d['cut'])
                self.x = x1
                self.y = y1

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
