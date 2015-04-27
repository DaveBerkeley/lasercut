
import math
import cmath

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

#
#

def radians(degrees):
    return math.pi * degrees / 180.0

#def degrees(rad):
#    return 180.0 * rad / math.pi

def rotate_2d(theta, x, y):
    """Rotate point by theta"""
    cangle = cmath.exp(theta * 1j)
    cx = cangle * complex(x, y)
    return cx.real, cx.imag

#
#

def distance_from_line(xy, line):
    # see http://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line#Line_defined_by_two_points
    x0, y0 = xy
    (x1, y1), (x2, y2) = line
    a = y2 - y1
    b = x2 - x1
    a = (a * a) + (b * b)
    q = math.sqrt(a)
    a = x0 * (y2 - y1)
    b = y0 * (x2 - x1)
    a = a - b + (x2 * y1) - (y2 * x1)
    return abs(a) / q

def distance(xy0, xy1):
    x0, y0 = xy0
    x1, y1 = xy1
    dx = x0 - x1
    dy = y0 - y1
    return math.sqrt((dx*dx) + (dy*dy))

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

    def cut(self):
        return self.data["cut"]

#
#

class Polygon:
    def __init__(self, xy=None):
        self.points = []
        self.arcs = []
        self.origin = xy

    def add(self, x, y):
        self.points.append((x, y))

    def add_arc(self, arc):
        self.arcs.append(arc)

    def copy(self):
        poly = Polygon(self.origin)
        poly.arcs = [ arc.copy() for ac in self.arcs ]
        for point in self.points:
            poly.add(*point)
        return poly

    def close(self):
        self.points.append(self.points[0])

    def lines(self):
        x0, y0 = self.points[0]
        for x, y in self.points[1:]:
            line = (x0, y0), (x, y)
            x0, y0 = x, y
            yield line

    def rotate(self, degrees):
        points = []
        rad = radians(degrees)
        for x, y in self.points:
            points.append(rotate_2d(rad, x, y))
        self.points = points
        for arc in self.arcs:
            arc.rotate(degrees)
        if self.origin:
            self.origin = rotate_2d(rad, x, y)

    def translate(self, dx, dy):
        points = []
        for x, y in self.points:
            points.append((x + dx, y + dy))
        self.points = points
        for arc in self.arcs:
            arc.translate(dx, dy)
        if self.origin:
            self.origin = self.origin[0] + dx, self.origin[1] + dy

    def draw(self, drawing, colour):
        for xy0, xy1 in self.lines():
            item = dxf.line(xy0, xy1, color=colour)
            drawing.add(item)
        for arc in self.arcs:
            arc.draw(drawing, colour)

#
#

class Rectangle(Polygon):
    def __init__(self, config, xy0, xy1):
        Polygon.__init__(self)

        x0, y0 = xy0
        x1, y1 = xy1
        self.add(x0, y0)
        self.add(x1, y0)
        self.add(x1, y1)
        self.add(x0, y1)
        self.close()

#
#

class Arc:

    def __init__(self, xy, radius, start_angle, end_angle):
        self.x, self.y = xy
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle

    def rotate(self, degrees):
        rad = radians(degrees)
        self.x, self.y = rotate_2d(rad, self.x, self.y)

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

    def copy(self):
        return Arc((self.x, self.y), self.radius, self.start_angle, self.end_angle)

    def draw(self, drawing, colour):
        item = dxf.arc(radius=self.radius, center=(self.x, self.y), startangle=self.start_angle, endangle=self.end_angle, color=colour)
        drawing.add(item)

    def __repr__(self):
        return "Arc(%s,%s,%s,%s,%s)" % (self.x, self.y, self.radius, self.start_angle, self.end_angle)

#
#

class Circle(Arc):
    def __init__(self, xy, radius):
        Arc.__init__(self, xy, radius, 0, 360)


#
#

class TCut:

    def __init__(self, w, d, shank, nut_w, nut_t, stress_hole=None):
        self.w = w
        self.d = d
        self.shank = shank
        self.nut_w = nut_w
        self.nut_t = nut_t
        self.stress_hole = stress_hole

    def make_elev(self, xy, orient):
        shape = Polygon()
        width = self.w / 2.0
        n_width = self.nut_w / 2.0
        shape.add(-width, 0)
        shape.add(-width, -self.shank)
        shape.add(-n_width, -self.shank)
        shape.add(-n_width, -(self.shank + self.nut_t))
        shape.add(-width, -(self.shank + self.nut_t))
        shape.add(-width, -self.d)

        shape.add(width, -self.d)
        shape.add(width, -(self.shank + self.nut_t))
        shape.add(n_width, -(self.shank + self.nut_t))
        shape.add(n_width, -self.shank)
        shape.add(width, -self.shank)
        shape.add(width, 0)

        if self.stress_hole:
            shape.add_arc(Circle((-n_width, -self.shank), self.stress_hole))
            shape.add_arc(Circle((n_width, -self.shank), self.stress_hole))

        shape.rotate(orient)
        shape.translate(*xy)
        shape.origin = xy

        return shape

#
#

def replace(line, shape):
    points = shape.points[:]
    start, end = points[0], points[-1]

    dstart = distance(line[0], start)
    dend = distance(line[0], end)

    if dend < dstart:
        points.reverse()
        start, end = end, start

    poly = Polygon()
    poly.add(*line[0])
    for point in points:
        poly.add(*point)

    poly.add(*line[1])
    return poly.lines()

#
#

def on_segment(xy, line):
    d = distance_from_line(xy, line)
    if d > 0.01:
        return False
    (x0, y0), (x1, y1) = line
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    # are we on the segment?
    return (x0 <= xy[0] <= x1) and (y0 <= xy[1] <= y1)

def splice(src, item):
    lines = []
    arcs = []
    for line in src.lines():
        if on_segment(item.origin, line):
            for subst in replace(line, item):
                lines.append(subst)
            arcs += item.arcs
        else:
            lines.append(line)

    shape = Polygon(src.origin)
    shape.add(*lines[0][0])
    for line in lines:
        shape.add(*line[1])
    shape.arcs = src.arcs[:]
    shape.arcs += [ arc.copy() for arc in arcs ]
    return shape

# FIN
