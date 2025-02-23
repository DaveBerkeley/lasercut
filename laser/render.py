#
#

import math
import cmath

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from .laser import radians, distance, Config

#
#

class Render:
    pass

#
#

class Block(object):

    def __init__(self, scad=None, text=""):
        self.scad = scad
        self.f = scad.f
        self.text = text

    def __enter__(self):
        self.scad.nest += 1
        print(self.text, "{", file=self.f)

    def __exit__(self, *args):
        self.scad.nest -= 1
        print("}", file=self.f)

class Difference(Block):
    def __init__(self, f):
        super().__init__(f, "difference()")

class Union(Block):
    def __init__(self, f):
        super().__init__(f, "union()")

class Intersection(Block):
    def __init__(self, f):
        super().__init__(f, "intersection()")

class Hull(Block):
    def __init__(self, f):
        super().__init__(f, "hull()")

class SCAD(Render):

    def __init__(self, filename="test.scad"):
        self.nest = 0
        if filename is None:
            import sys
            self.f = sys.stdout
        else:
            self.f = open(filename, "w")

        # enclose everything in a "module filename() {"
        path = filename.split('/')[-1]
        self.module_name = path.rsplit('.', 1)[0]
        print("module", self.module_name, "() {", file=self.f)

    def save(self):
        # end module definition and invoke it
        print("}", file=self.f)
        print(self.module_name, "();", file=self.f)
        self.f.close()

    def color_to_line(self, color):
        # TODO : map colour to line width
        return 1

    def dotted(self, color):
        return color == Config.dotted_colour

    def comment(self, *args):
        print("//", *args, file=self.f)

    def xform(self, fn, **kwargs):
        print(f"{fn}(", file=self.f, end="")
        first = True
        for k, v in kwargs.items():
            if not first:
                print(",", file=self.f, end="")
            first = False
            # booleans are different in Python/scad
            if v is True:
                v = "true"
            elif v is False:
                v = "false"
            print(f"{k} = {v}", file=self.f, end="")
        print(")", file=self.f)

    def function(self, fn, **kwargs):
        self.xform(fn, **kwargs);
        print(";", file=self.f)

    def cylinder(self, h=None, r1=None, r2=None):
        if r2 is None:
            r2 = r1
        self.function("cylinder", h=h, r1=r1, r2=r2)

    def circle(self, radius=None, center=None, color=None):
        width = self.color_to_line(color)
        if center:
            self.xform("translate", v=[ center[0], center[1], 0 ])

        self.xform("linear_extrude", height=width)
        with Difference(self):
            self.function("circle", r=radius+(width/2.0))
            rr = radius - (width/2.0)
            if rr > 0.0:
                self.function("circle", r=rr)

    def arc(self, radius=None, center=None, startangle=None, endangle=None, color=None):
        #print(f"// arc(r={radius}, s={startangle}, e={endangle})")

        if startangle < 0.0:
            startangle += 360
            endangle += 360
        elif endangle < startangle:
            endangle += 360

        dotted = self.dotted(color)
        width = self.color_to_line(color)
        if center:
            self.xform("translate", v=[ center[0], center[1], 0 ])
        with Union(self):
            step = 1.0 # !!!!
            a1 = startangle
            while (a1+step) < endangle:
                a2 = a1 + step
                xy0 = [ radius * math.cos(radians(a1)), radius * math.sin(radians(a1)) ]
                xy1 = [ radius * math.cos(radians(a2)), radius * math.sin(radians(a2)) ]
                a1 += step
                if dotted:
                    self.xform("linear_extrude", height=width)
                    self.xform("translate", v=xy0)
                    self.function("circle", r=width/2.0)
                else:
                    self.line(xy0, xy1, color=color)

    def line(self, xy0, xy1, color=None):
        width = self.color_to_line(color)
        za = complex(*xy0)
        zb = complex(*xy1)
        ph = cmath.phase(za - zb)
        u = cmath.rect(width/2.0, ph + cmath.pi/2.0)
        points = [
            [ (za+u).real, (za+u).imag ],
            [ (za-u).real, (za-u).imag ],
            [ (zb-u).real, (zb-u).imag ],
            [ (zb+u).real, (zb+u).imag ],
        ]
        points.append(points[0])
        self.xform("linear_extrude", height=width)
        with Union(self):
            self.function("polygon", points=points)
            for xy in [ xy0, xy1 ]:
                self.xform("translate", v=list(xy) )
                self.function("circle", r=width/2)

    def text(self, text, insert=None, rotation=0, color=None, **kwargs):
        #print(f"'{text}'", insert, rotation, color, kwargs)
        width = kwargs.get("depth", 1)
        h = kwargs.get("height", 1)
        self.xform("linear_extrude", height=width)
        if insert:
            z = complex(*insert)
            # move the point 'h' nearer to the centre
            ph = cmath.phase(z)
            zz = cmath.rect(h, ph)
            z -= zz
            self.xform("translate", v=[ z.real, z.imag, ])
        if rotation:
            self.xform("rotate", a=rotation)
        self.function("text", text=f'"{text}"', size=h)

    @staticmethod
    def drawing(*args):
        return SCAD(*args)

#
#

class DXF(Render):

    def __init__(self, filename="test.dxf"):
        assert filename, "can't output DXF to stdout"
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

#
#

class PDF:
    def __init__(self, path):
        assert path, "can't output PDF to stdout"
        print(path)
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        self.c = canvas.Canvas(path, pagesize=A4)
        self.set_defaults()
        self.mm = mm

    def mm2p(self, *args):
        # mm to points (1/72 inch!)
        def scale(x):
            return x * self.mm / 2
        if len(args) == 1:
            return scale(args[0])
        # mm to point size
        return [ scale(x) for x in args ]

    def set_defaults(self):
        from reportlab.lib.pagesizes import A4
        self.c.translate(A4[0]/2, A4[1]/2)
        self.c.setLineWidth(0.5)

    def tocolor(self, color):
        from reportlab.lib.colors import black, red, grey, green, blue
        lut = {
            Config.cut_colour : red,
            Config.draw_colour : blue,
            Config.dotted_colour : grey,
            Config.engrave_colour : green,
            Config.thick_colour : black,
            Config.thin_colour : grey,
            #None : red,
        }
        return lut[color]

    def set_color(self, color):
        self.c.setStrokeColor(self.tocolor(color))
        if color == Config.dotted_colour:
            self.c.setDash(1, 1)
        else:
            self.c.setDash(1, 0)

    def circle(self, radius=None, center=None, color=None):
        x, y = center or (0, 0)
        self.set_color(color)
        self.c.circle(*self.mm2p(x, y, radius))

    def line(self, xy0, xy1, color=None):
        self.set_color(color)
        self.c.line(*self.mm2p(xy0[0], xy0[1], xy1[0], xy1[1]))

    def arc(self, radius=None, center=None, startangle=None, endangle=None, color=None):
        if (startangle > 0) and (endangle < 0):
            endangle += 360
        x, y = center or (0, 0)
        s = startangle
        e = endangle - s
        if e < 0:
            e = (endangle + 360) - s
        self.set_color(color)
        self.c.arc(*self.mm2p(x-radius, y-radius, x+radius, y+radius), startAng=s, extent=e)

    def text(self, text, insert=None, rotation=0, color=None, **kwargs):
        self.c.saveState()
        x, y = insert or (0, 0)
        height = kwargs['height']
        self.c.setFontSize(int(self.mm2p(height)))
        self.set_color(color)
        obj = self.c.beginText()
        if 'adjust' in kwargs:
            # need to move the x,y location height nearer the origin
            z = complex(x, y)
            r = cmath.polar(z)
            z = cmath.rect(r[0]-height, r[1])
            x, y = z.real, z.imag
        self.c.translate(*self.mm2p(x, y))
        self.c.rotate(rotation)
        obj.textOut(text)
        self.c.drawText(obj)
        self.c.restoreState()

    def save(self):
        self.c.showPage()
        self.c.save()

    @staticmethod
    def drawing(*args):
        import reportlab
        return PDF(*args)

# FIN
