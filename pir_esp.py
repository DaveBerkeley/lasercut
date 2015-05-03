#!/usr/bin/python

import sys

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import TCut, Text, splice, cutout

from parts import ESP_Olimex_Dev as ESP
from parts import PIR_DYPME003 as PIR
from parts import Temperature_DS18b20 as Temperature
from parts import Hanger

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
    feet_w = 15
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

    def make_side_posn(dx, dy, horiz=True):
        w = Collection()
        c = Rectangle((0, 0), (dx, dy), colour=Config.draw_colour)
        w.add(c)
        c = Polygon((0, 0), colour=Config.dotted_colour)
        c.add(0, 0)
        if horiz:
            c.add(dx, 0)
            c.translate(0, dy / 2.0)
        else:
            c.add(0, dy)
            c.translate(dx / 2.0, 0)
        w.add(c)
        return w

    if draw:
        # draw the side positions
        dy = front_hin + (3 * thick)
        w = make_side_posn(thick, dy, horiz=False)
        w.translate(overhang, 0)
        work.add(w)
        w = make_side_posn(thick, dy, horiz=False)
        w.translate(front_wout - overhang - thick, 0)
        work.add(w)

        # draw top/bottom and middle plates
        dx = front_win + thick + thick
        w = make_side_posn(dx, thick, horiz=True)
        w.translate(overhang, 0)
        work.add(w)
        w = make_side_posn(dx, thick, horiz=True)
        w.translate(overhang, front_hin + thick + thick)
        work.add(w)
        w = make_side_posn(dx, thick, horiz=True)
        w.translate(overhang, ESP.h + thick)
        work.add(w)

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

    if 1:
        d1, d2, d = 3, 6, 6
        h = Hanger(r1=d1/2.0, r2=d2/2.0, d=d)
        c = h.make()
        x = front_wout / 2.0
        c.translate(x, ESP.h + feet + thick + d2 + 1)
        work.add(c)

    return work

#
#

def add_cutouts(work, locs, template):
    for x, y, rot in locs:
        c = template.copy()
        c.rotate(rot)
        c.translate(x, y)
        work = splice(work, c)
    return work


def make_t_holder(draw, is_top=False, is_mid=False, is_bot=False):
    work = Collection()

    top_h = ESP.max_d
    t_holder_w = 18
    t_holder_d = 12
    inset = t_holder_d / 2.0
    inner = 6

    if is_bot:
        c = Rectangle((0, 0), (front_win, top_h)) 
        work.add(c)
    else:
        c = Polygon()
        c.add(front_win, top_h)
        if is_mid:
            c.add(front_win - inner, top_h)
            c.add(front_win - inner, inner)
            c.add(inner, inner)
            c.add(inner, top_h)
        c.add(0, top_h)
        c.add(0, 0)
        c.add(front_win, 0)
        c.add(front_win, top_h - inset)
        work.add(c)

        w = Collection()
        c = Polygon()
        c.add(0, t_holder_d / 2.0)
        c.add(t_holder_w + thick - (2 * inset), t_holder_d / 2.0)
        w.add(c)

        c = Polygon()
        c.add(t_holder_w + thick - inset, t_holder_d)
        c.add(0, t_holder_d)
        w.add(c)

        p = Polygon()
        if is_top:
            r = Temperature.dia / 2.0
        elif is_mid:
            r = Temperature.outer_1 / 2.0
        d = Circle((0, 0), r)
        d.translate(t_holder_w + thick - inset, t_holder_d - inset)
        p.add_arc(d)

        d = Arc((0, 0), inset, 180, 90)
        d.translate(t_holder_w + thick - inset, t_holder_d - inset)
        p.add_arc(d)

        w.add(p)
        w.translate(front_win, top_h - t_holder_d)
        work.add(w)

    dx = tab_len / 2.0
    cut_locs = [
        # bot
        [ front_win / 3.0, 0, 180 ],
        [ 2 * front_win / 3.0, 0, 180 ],
        [ front_win / 3.0, top_h, 0 ],
        [ 2 * front_win / 3.0, top_h, 0 ],
        # sides
        [ 0, dx, 90 ],
        [ 0, top_h - dx, 90 ],
        [ front_win, dx, 270 ],
    ]

    if is_bot:
        a = [ front_win, top_h - dx, 270 ]
        cut_locs.insert(0, a)

    template = cutout(tab_len, thick)
    work = add_cutouts(work, cut_locs, template)

    if 0: # draw:
        c = Rectangle((0, 0), (front_win, top_h), colour=Config.draw_colour)
        work.add(c)

    if is_bot:
        c = Text((0, 0), "PIR V1.0", height=3.0, colour=Config.engrave_colour)
        c.translate(10, 10)
        work.add(c)

    return work

#
#

config = Config()

drawing = dxf.drawing("test.dxf")

draw = True

tab_len = 5

work = make_front(draw)
work.draw(drawing, config.cut())

dx = front_wout + spacing + thick
dy = ESP.max_d

work = make_t_holder(draw, is_mid=True)
work.translate(dx, thick)
work.draw(drawing, config.cut())

work = make_t_holder(draw, is_top=True)
work.translate(dx, dy + spacing + (1 * thick))
work.draw(drawing, config.cut())

work = make_t_holder(draw, is_bot=True)
work.translate(dx, (2 * (dy + spacing)) + (3 * thick))
work.draw(drawing, config.cut())

drawing.save()

# FIN
