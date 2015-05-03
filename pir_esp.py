#!/usr/bin/python

import sys

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import TCut, Text, splice, cutout

from parts import ESP_Olimex_Dev as ESP
from parts import PIR_DYPME003 as PIR
from parts import Temperature_DS18b20 as Temperature

#

thick = 3
spacing = 1

x_margin = 10
y_margin = 20

def move_margin(work):
    work.translate(x_margin, y_margin)

#
#   Foot

def make_foot(work_w):
    feet_w = 20
    foot = Collection()
    c = Polygon()
    c.add(0, 0)
    c.add(0, - feet)
    c.add(feet_w, - feet)

    # inner curve
    a = Arc((feet_w + feet, -feet), feet, 90, 180)
    c.add_arc(a)
    foot.add(c)

    d = c.copy()
    d.reflect_v()
    d.translate(work_w, 0)
    foot.add(d)

    c = Polygon()
    c.add(feet_w + feet, 0)
    c.add(work_w - feet_w - feet, 0)
    foot.add(c)

    return foot

#
#

feet = 6
overhang = 3

front_win = ESP.w
front_hin = ESP.h + PIR.h

front_hout = front_hin + (3 * thick) + overhang
front_wout = front_win + (2 * thick) + (2 * overhang)

def make_front(draw):
    work = Collection()

    c = Polygon()
    c.add(0, 0)
    c.add(0, front_hout)
    c.add(front_wout, front_hout)
    c.add(front_wout, 0)

    work.add(c)

    if draw:
        # draw the side positions
        dy = front_hin + (3 * thick) + overhang
        w = Collection()
        c = Rectangle((0, 0), (thick, dy), colour=Config.draw_colour)
        w.add(c)
        c = Polygon((0, 0), colour=Config.dotted_colour)
        c.add(0, 0)
        c.add(0, dy)
        c.translate(thick / 2.0, 0)
        w.add(c)
        d = w.copy()
        w.translate(overhang, 0)
        work.add(w)
        d.translate(front_wout - overhang - thick, 0)
        work.add(d)
        # draw top/bottom and middle plates
        w = Collection()
        dx = front_win + thick + thick
        c = Rectangle((0, 0), (dx, thick), colour=Config.draw_colour)
        c.translate(thick, 0)
        w.add(c)
        c = Polygon((0, 0), colour=Config.dotted_colour)
        c.add(0, 0)
        c.add(dx, 0)
        c.translate(overhang, thick / 2.0)
        w.add(c)
        d = w.copy()
        work.add(w)
        d.translate(0, front_hin + thick + thick)
        work.add(d)

    foot = make_foot(front_wout)
    work.add(foot)
    work.translate(0, feet)

    if 1:
        esp = ESP().make(draw)
        esp.translate(overhang + thick, feet + thick)
        work.add(esp)

    if 1:
        pir = PIR().make(draw)
        x = (front_wout - PIR.w) / 2.0
        pir.translate(x, feet + thick + thick + ESP.h)
        work.add(pir)

    return work

#
#

def make_t_holder(is_top):
    work = Collection()

    top_h = ESP.max_d
    t_holder_w = 18
    t_holder_d = 12
    inset = t_holder_d / 2.0
    inner = 6

    c = Polygon()
    c.add(front_win, top_h)
    if not is_top:
        c.add(front_win - inner, top_h)
        c.add(front_win - inner, inner)
        c.add(inner, inner)
        c.add(inner, top_h)
    c.add(0, top_h)
    c.add(0, 0)
    c.add(front_win, 0)
    c.add(front_win, top_h - t_holder_d)
    work.add(c)

    w = Collection()
    c = Polygon()
    c.add(0, 0)
    c.add(t_holder_w + thick - inset, 0)
    w.add(c)

    c = Polygon()
    c.add(t_holder_w + thick - inset, t_holder_d)
    c.add(0, t_holder_d)
    w.add(c)

    p = Polygon()
    if is_top:
        r = Temperature.dia / 2.0
    else:
        r = Temperature.outer_1 / 2.0
    d = Circle((0, 0), r)
    d.translate(t_holder_w + thick - inset, t_holder_d - inset)
    p.add_arc(d)

    d = Arc((0, 0), inset, 270, 90)
    d.translate(t_holder_w + thick - inset, t_holder_d - inset)
    p.add_arc(d)

    w.add(p)
    w.translate(front_win, top_h - t_holder_d)
    work.add(w)
    return work

#
#

#
#

config = Config()

drawing = dxf.drawing("test.dxf")

draw = True

work = make_front(draw)
work.draw(drawing, config.cut())

work = make_t_holder(False)
work.translate(front_wout + spacing, 0)
work.draw(drawing, config.cut())

work = make_t_holder(True)
work.translate(front_wout + spacing, ESP.max_d + spacing)
work.draw(drawing, config.cut())

drawing.save()

# FIN
