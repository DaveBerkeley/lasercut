#!/usr/bin/python

import sys
import math

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import radians, degrees, angle, rotate_2d, splice, corner
from render import DXF as dxf

import ops

#
#

def curve(x0, y0, r, a0, a1, min_d=0.2):
    arc = Arc((x0, y0), r, a0, a1)
    return ops.arc_to_poly(arc)

def curves(x0, y0, r0, r1, a0, a1):
    p = curve(x0, y0, r0, a0, a1)
    c = curve(x0, y0, r1, a0, a1)
    c.points.reverse()
    p.add_poly(c)
    p.close()
    return p

#
#

def design():
    a_step = 5
    step = 8
    strip = 2

    rect = Rectangle((0, 0), (w*2, strip))

    rects = []

    for angle in range(0, 90, a_step):
        rr = rect.copy()
        rr.rotate(angle)
        rects.append(rr)

    diag = int(abs(complex(w, h)))
    for d in range(step * 3, int(diag), step):
        c = curves(edge, edge, d, d + strip, 0, 91)
        rects.append(c)

    shape = ops.Shape(rects[0])

    for r in rects[1:]:
        shape = shape.union(ops.Shape(r))

    e = edge / 2
    r = Rectangle((e, e), (w-e, h-e))
    shape = shape.intersection(ops.Shape(r))
    return shape

def x_design():

    step = 20
    strip = 2
    shape = None
    e = edge / 2
    for x in range(e, w-e, 20):
        r = Rectangle((x, e), (x+strip, h-e))
        if shape is None:
            shape = ops.Shape(r)
        else:
            shape = shape.union(ops.Shape(r))
    for y in range(e, h-e, 20):
        r = Rectangle((e, y), (w-e, y+strip))
        shape = shape.union(ops.Shape(r))

    return shape

def band(x, y, r, strip):
    c = Circle((x, y), r)
    shape = ops.Shape(c)
    c = Circle((x, y), r+strip)
    shape = shape.symmetric_difference(ops.Shape(c))
    return shape

def xdesign():
    strip = 2

    def pool(x, y):
        shape = None
        for r in range(80, 80, 10):
            c = band(x, y, r, strip)
            if shape:
                shape = shape.union(c)
                break
            else:
                shape = c
        return shape

    xy = [
        (50, 50), (100, 100), (45, 120),
    ]
    shape = None
    for x, y in xy:
        for r in range(50, 10, -10):
            r = band(x, y, r, strip)
            if shape:
                shape = shape.union(r)
            else:
                shape = r
    return shape

def xdesign():

    def star(x0, y0, d):
        n = 5
        p = Polygon()
        for angle in range(0, 360, 360/n):
            print angle
            x, y = rotate_2d(radians(angle), 0, d)
            p.add(x, y)
            angle += 180/n
            x, y = rotate_2d(radians(angle), 0, 2.0 * d / 5.0)
            p.add(x, y)
        p.close()
        p.translate(x0, y0)
        return p

    def make(x0, y0, d):
        s = star(x0, y0, d)
        shape = ops.Shape(s)
        s = star(x0, y0, d-5)
        shape = shape.symmetric_difference(ops.Shape(s))
        return shape

    shape = make(50, 50, 80)
    s = make(150, 150, 80)
    shape = shape.union(s)
    s = make(100, 80, 50)
    shape = shape.union(s)
    return shape

def xdesign():

    shape = None
    for x in range(10, w, 18):
        for y in range(10, h, 18):
            s = band(x, y, 14, 3)
            if shape:
                shape = shape.union(s)
            else:
                shape = s
    return shape

#
#   Make the side pieces

def make_side():
    shape = design()

    # clip the design
    e = edge/2
    r = Rectangle((e, e), (w-e, h-e))
    shape = shape.intersection(ops.Shape(r))

    # frame the design

    r = Rectangle((edge, edge), (w-edge, h-edge))
    s = ops.Shape(r)
    r = Rectangle((0, -bot), (w, h+top))

    s = s.symmetric_difference(ops.Shape(r))
    shape = shape.union(s)

    work = shape.get()
    work.translate(0, bot)

    # cut the tabs

    if 1:
        tab_len = (h+top+bot)/tabs
        i, y = 0, 0
        while y < (h+top+bot):
            if (i % 2) == 0:
                x = 0
                dx = -thick
            else:
                x = w
                dx = thick
            p = Polygon((x, y + (tab_len/2)))
            p.add(x, y)
            p.add(x+dx, y)
            p.add(x+dx, y+tab_len)
            p.add(x, y+tab_len)
            work = splice(work, p)
            i += 1
            y += tab_len

    # make the feet

    if 1:
        foot_w = w / 5
        foot_h = bot * 0.2
        p = Polygon((w/2, 0))
        p.add(foot_w, 0)
        p.add(foot_w, foot_h)
        p.add(w - foot_w, foot_h)
        p.add(w - foot_w, 0)

        work = splice(work, p)

        work = corner(work, (foot_w, foot_h), foot_h)
        work = corner(work, (w-foot_w, foot_h), foot_h)

    # cut slots for the middle sections

    info = get_slots()
    slot_w = info["w"]
    p = Rectangle((0, 0), (slot_w, thick))
    p.translate(-slot_w / 2, -thick / 2)
    for y in [ bot, bot + h ]:
        for x in info["d"]:
            r = p.copy()
            r.translate(x, y)
            work.add(r)

    # move over so lhs is at 0
    work.translate(thick, 0)
    return work

def get_slots():
    slot_w = w / 8.0
    return {
        "w" : slot_w,
        "d" : [  w/4.0, 2*w/4.0, 3*w/4.0 ]
    }

def make_middle(is_top=True):
    work = Collection()
    p = Rectangle((0, 0), (w, w))
    work.add(p)

    # add the tabs
    info = get_slots()
    slot = info["w"]
    s = slot/2.0
    p = Polygon()
    p.add(-s, 0)
    p.add(-s, -thick)
    p.add(s, -thick)
    p.add(s, 0)

    for x in info["d"]:
        r = p.copy()
        r.translate(x, 0)
        work = splice(work, r)

        r = p.copy()
        r.rotate(180)
        r.translate(x, w)
        work = splice(work, r)

        r = p.copy()
        r.rotate(270)
        r.translate(0, x)
        work = splice(work, r)

        r = p.copy()
        r.rotate(90)
        r.translate(w, x)
        work = splice(work, r)

    if not is_top:
        # hole for lamp fitting
        c = LampHolder().make()
        c.translate(w/2, w/2)
        work.add(c)

        # holes for ventilation
        for angle in range(0, 360, 360/8):
            d = w * 0.35
            c = Circle((d, 0), small_vent_r)
            c.rotate(angle)
            c.translate(w/2, w/2)
            work.add(c)

    if is_top:
        c = Circle((w/2, w/2), big_vent_r)
        work.add(c)

    return work

class LampHolder:

    outer_r = 28.0 / 2
    inner_r = 26.0 / 2

    def make(self):
        work = Collection()
        d = math.sqrt((self.outer_r * self.outer_r) - (self.inner_r * self.inner_r))
        p = Polygon()
        p.add(-d, self.inner_r)
        p.add(d, self.inner_r)
        work.add(p)
        p = Polygon()
        p.add(-d, -self.inner_r)
        p.add(d, -self.inner_r)
        work.add(p)

        a = degrees(angle(self.inner_r, d))
        c = Arc((0, 0), self.outer_r, 270+a, 90-a)
        work.add(c)
        c = Arc((0, 0), self.outer_r, 90+a, 270-a)
        work.add(c)
        return work

#
#

if __name__ == "__main__":

    config = Config()

    drawing = dxf.drawing("test.dxf")

    w = 130.0
    h = 180.0
    thick = 3
    spacing = 1
    edge = 8
    tabs = 20
    tab_d = thick
    top = 6
    bot = 60
    big_vent_r = 0.8 * w/2
    # lamp fitting
    lamp_r = 14.0, 13.0
    small_vent_r = 10

    if len(sys.argv) == 1:
        work = make_side()
    else:
        work = make_middle(True)
        work.translate(0, w + (2 * thick) + spacing)
        w = make_middle(False)
        work.add(w)

    # for the printer
    work.translate(10, 20)
    work.draw(drawing, config.cut())

    drawing.save()

# FIN
