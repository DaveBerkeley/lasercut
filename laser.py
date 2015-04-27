
# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#

class Material:

    def __init__(self, w, h, t):
        self.width = w
        self.height = h
        self.thickness = t

#
#

class Config:

    def __init__(self, **kwargs):
        self.data = kwargs
        self.data["cut"] = 3
        self.data["engrave"] = 2
        self.data["kisscut"] = 1

    def offset(self):
        return 0.0 # TODO
        kerf = self.data["kerf"]
        return kerf / 2.0

    def cut(self):
        return self.data["cut"]

#
#

class Polygon:
    def __init__(self):
        self.points = []

    def add(self, x, y):
        self.points.append((x, y))

    def close(self):
        self.points.append(self.points[0])

    def lines(self):
        x0, y0 = self.points[0]
        for x, y in self.points[1:]:
            line = (x0, y0), (x, y)
            x0, y0 = x, y
            yield line

    def draw(self, drawing, colour):
        for xy0, xy1 in self.lines():
            item = dxf.line(xy0, xy1, color=colour)
            drawing.add(item)

#
#

class Rectangle(Polygon):
    def __init__(self, config, xy0, xy1, hole):
        Polygon.__init__(self)
        offset = config.offset()
        if not hole:
            offset = -offset

        x0, y0 = xy0[0] + offset, xy0[1] + offset
        x1, y1 = xy1[0] - offset, xy1[1] - offset
        self.add(x0, y0)
        self.add(x1, y0)
        self.add(x1, y1)
        self.add(x0, y1)
        self.close()

#
#

class TCut:

    def __init__(self, config, nut_size, nut_length):
        self.config = config
        self.nut_size = nut_size
        self.nut_length = nut_length

    def set_drawing(self, drawing):
        self.drawing = drawing

    def draw_elev(self, x, y):
        pass

    def draw_plan(self, x, y):
        pass

# FIN
