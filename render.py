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

# FIN
