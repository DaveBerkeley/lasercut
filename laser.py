
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

    cut_colour = 3
    draw_colour = 4
    dotted_colour = 5
    engrave_colour = 2

    def __init__(self, **kwargs):
        self.data = kwargs

    def cut(self):
        return self.cut_colour

#
#

class Polygon:
    def __init__(self, xy=(0, 0), **kwargs):
        self.points = []
        self.arcs = []
        self.origin = xy
        self.kwargs = kwargs

    def add(self, x, y):
        self.points.append((x, y))

    def add_arc(self, arc):
        self.arcs.append(arc)

    def copy(self):
        poly = Polygon(self.origin)
        poly.arcs = [ arc.copy() for arc in self.arcs ]
        for point in self.points:
            poly.add(*point)
        poly.kwargs = self.kwargs
        return poly

    def close(self):
        self.points.append(self.points[0])

    def lines(self):
        if self.points:
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
            self.origin = rotate_2d(rad, self.origin[0], self.origin[1])

    def translate(self, dx, dy):
        points = []
        for x, y in self.points:
            points.append((x + dx, y + dy))
        self.points = points
        for arc in self.arcs:
            arc.translate(dx, dy)
        if self.origin:
            self.origin = self.origin[0] + dx, self.origin[1] + dy

    def move(self, x, y):
        self.translate(x - self.origin[0], y - self.origin[1])

    def reflect_v(self):
        points = []
        for point in self.points:
            points.append((-point[0], point[1]))
        self.points = points
        def angle(a):
            if 0 <= a < 180:
                return 180 - a
            return a - 180
        for arc in self.arcs:
            arc.x = -arc.x
            arc.start_angle = angle(arc.start_angle)
            arc.end_angle = angle(arc.end_angle)
            arc.start_angle, arc.end_angle = arc.end_angle, arc.start_angle

    def extent(self):
        class Extent:
            def __init__(self):
                self.mina = None
                self.maxa = None
            def add(self, a):
                if self.mina is None:
                    self.mina = a
                    self.maxa = a
                    return
                if a < self.mina:
                    self.mina = a
                elif a > self.maxa:
                    self.maxa = a

        xx = Extent()
        yy = Extent()
        for x, y in self.points:
            xx.add(x)
            yy.add(y)
        # TODO : needs extent of arcs too
        return Rectangle((xx.mina, yy.mina), (xx.maxa, yy.maxa))

    def draw(self, drawing, colour):
        colour = self.kwargs.get("colour", colour)
        for xy0, xy1 in self.lines():
            item = dxf.line(xy0, xy1, color=colour)
            drawing.add(item)
        for arc in self.arcs:
            arc.draw(drawing, colour)

#
#

class Rectangle(Polygon):
    def __init__(self, xy0, xy1, **kwargs):
        x0, y0 = xy0
        x1, y1 = xy1
        Polygon.__init__(self, (x0, y0), **kwargs)
        self.corner = x1, y1

        self.add(x0, y0)
        self.add(x1, y0)
        self.add(x1, y1)
        self.add(x0, y1)
        self.close()
        self.str = "Rectangle((%d,%d),(%d,%d))" % (x0, y0, x1, y1)

    def corners(self):
        return self.points[:-1]

    def __repr__(self):
        return self.str

#
#

class Arc:

    def __init__(self, xy, radius, start_angle, end_angle, **kwargs):
        self.x, self.y = xy
        self.radius = radius
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.kwargs = kwargs

    def rotate(self, degrees):
        rad = radians(degrees)
        self.x, self.y = rotate_2d(rad, self.x, self.y)
        # rotate start/end angles
        # TODO : check for < 0, or > 360 condition
        self.start_angle += degrees
        self.end_angle += degrees

    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

    def move(self, x, y):
        self.x  = x
        self.y = y

    def copy(self):
        a = Arc((self.x, self.y), self.radius, self.start_angle, self.end_angle)
        a.kwargs = self.kwargs
        return a

    def draw(self, drawing, colour):
        colour = self.kwargs.get("colour", colour)
        item = dxf.arc(radius=self.radius, center=(self.x, self.y), startangle=self.start_angle, endangle=self.end_angle, color=colour)
        drawing.add(item)

    def __repr__(self):
        return "Arc(%s,%s,%s,%s,%s)" % (self.x, self.y, self.radius, self.start_angle, self.end_angle)

#
#

class Circle(Arc):
    def __init__(self, xy, radius, **kwargs):
        Arc.__init__(self, xy, radius, 0, 360, **kwargs)

#
#

class Collection:
    def __init__(self, work=None):
        self.data = []
        self.origin = None
        self.arcs = []
        if work:
            self.add(work)
    def add(self, obj):
        self.data.append(obj)
    def draw(self, drawing, colour):
        for data in self.data:
            data.draw(drawing, colour)
    def rotate(self, degrees):
        for data in self.data:
            data.rotate(degrees)
    def translate(self, dx, dy):
        for data in self.data:
            data.translate(dx, dy)
    def move(self, x, y):
        for data in self.data:
            data.move(x, y)
    def lines(self):
        for data in self.data:
            for line in data.lines():
                yield line
    def copy(self):
        c = Collection()
        for data in self.data:
            c.add(data.copy())
        return c

#
#   Text

class Text:

    def __init__(self, xy, text, **kwargs):
        self.origin = xy
        self.text = text
        self.rot = 0
        self.kwargs = kwargs
    def translate(self, dx, dy):
        self.origin = self.origin[0] + dx, self.origin[1] + dy
    def rotate(self, degrees):
        self.rot += degrees
    def draw(self, drawing, colour):
        colour = self.kwargs.get("colour", colour)
        text = dxf.mtext(self.text, insert=self.origin, rotation=self.rot, color=colour, **self.kwargs)
        drawing.add(text)

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

    def make_plan(self, xy, orient):
        shape = Polygon()
        shape.add_arc(Circle((0, 0), self.w / 2.0))
        shape.rotate(orient)
        shape.translate(*xy)
        shape.origin = xy
        return shape

#
#

def corner(poly, xy, radius):
    # TODO
    return poly
    c = Collection()

    # find the lines touching xy
    lines = []
    for i in range(len(poly.points)-1):
        line = poly.points[i:i+2]
        if (line[0] == xy) or (line[1] == xy):
            lines.append(line)

    print lines
    c.add(poly)
    c.add(Circle(xy, radius))

    return c

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

def on_segment(xy, line, margin=0.01):
    d = distance_from_line(xy, line)
    if d > margin:
        return False
    (x0, y0), (x1, y1) = line
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    # are we on the segment?
    def within(x, x0, x1):
        if x0 > x1:
            x0, x1 = x1, x0
        return (x0-margin) <= x <= (x1+margin)
    return within(xy[0], x0, x1) and within(xy[1], y0, y1)

def find_hit(parent, item):
    for shape in parent.data:
        name = shape.__class__.__name__ 
        if name in [ "Polygon", "Rectangle" ]:
            for line in shape.lines():
                if on_segment(item.origin, line):
                    return parent, shape
        elif name == "Collection":
            p, shape = find_hit(shape, item)
            if shape:
                return p, shape
    return parent, None

def change_shape(parent, old, new):
    data = []
    for d in parent.data:
        if d == old:
            data.append(new)
        else:
            data.append(d)
    parent.data = data

def splice(parent, item):
    p, src = find_hit(parent, item)
    if src:
        w = splice_inner(src, item)
        change_shape(parent, src, w)
    else:
        print "no match found for", item
    return parent

def splice_inner(src, item):
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

#
#

def cutout(width, depth):
    poly = Polygon()
    width /= 2.0
    poly.add(-width, 0)
    poly.add(-width, depth)
    poly.add(width, depth)
    poly.add(width, 0)
    poly.origin = 0, 0
    return poly

#
#

def hinge(work, xy0, xy1, on, off, pitch):
    c = Collection()
    c.add(work)

    def frange(a, b, step):
        while a < b:
            yield a
            a += step

    y0, y1 = xy0[1], xy1[1]
    x0, x1 = xy0[0], xy1[0]
    for x in frange(x0, x1, pitch*2):
        y = y0
        poly = Polygon()
        poly.add(x, y)
        y += (on+off) / 2.0 # for the first cut
        poly.add(x, y)
        y += off
        c.add(poly)
        while (y+on) < y1:
            poly = Polygon()
            poly.add(x, y)
            y += on
            poly.add(x, y)
            y += off
            c.add(poly)
        poly = Polygon()
        poly.add(x, y)
        poly.add(x, y1)
        c.add(poly)
    for x in frange(x0+pitch, x1, pitch*2):
        for y in frange(y0+off, y1, on+off):
            poly = Polygon()
            poly.add(x, y)
            poly.add(x, min(y+on, y1-off))
            c.add(poly)

    return c

# FIN
