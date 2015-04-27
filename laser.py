
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

    def __init__(self, w, d, shank, nut_w, nut_t):
        self.w = w
        self.d = d
        self.shank = shank
        self.nut_w = nut_w
        self.nut_t = nut_t

    def make_elev(self, xy, orient):
        shape = Polygon()
        x, y = xy
        width = self.w / 2.0
        n_width = self.nut_w / 2.0
        shape.add(x - width, y)
        shape.add(x - width, y - self.shank)
        shape.add(x - n_width, y - self.shank)
        shape.add(x - n_width, y - (self.shank + self.nut_t))
        shape.add(x - width, y - (self.shank + self.nut_t))
        shape.add(x - width, y - self.d)

        shape.add(x + width, y - self.d)
        shape.add(x + width, y - (self.shank + self.nut_t))
        shape.add(x + n_width, y - (self.shank + self.nut_t))
        shape.add(x + n_width, y - self.shank)
        shape.add(x + width, y - self.shank)
        shape.add(x + width, y)
        return shape

# FIN
