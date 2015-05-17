#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import TCut, Text, splice, cutout, corner
from render import DXF as dxf

from parts import ESP_Olimex_Dev as ESP
from parts import PIR_DYPME003 as PIR
from parts import Temperature_DS18b20 as Temperature
from parts import Hanger
from parts import M3

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
    feet_less = 2
    rad = feet - feet_less
    foot = Collection()
    c = Polygon()
    c.add(0, 0)
    c.add(0, - feet)
    c.add(feet_w, - feet)

    # inner curve
    a = Arc((feet_w + rad, -feet), rad, 90, 180)
    c.add_arc(a)
    foot.add(c)

    d = c.copy()
    d.reflect_v()
    d.translate(work_w, 0)
    foot.add(d)

    c = Polygon()
    c.add(feet_w + rad, -feet_less)
    c.add(work_w - feet_w - rad, -feet_less)
    foot.add(c)

    return foot

#
#

feet = 6
overhang = 3

# low and hi sections (ESP / PIR)
margin = 1
lo_h = ESP.h + (2 * margin)
lo_w = ESP.w + margin
hi_h = PIR.h + (2 * margin)
hi_w = PIR.w + (2 * margin)

front_win = max(lo_w, hi_w)
front_hin = lo_h + hi_h

front_hout = front_hin + (3 * thick) + overhang
front_wout = front_win + (2 * thick) + (2 * overhang)

def make_front(draw, tab_locs, back=False):
    work = Collection()

    c = Polygon()
    c.add(0, 0)
    c.add(0, front_hout)
    c.add(front_wout, front_hout)
    c.add(front_wout, 0)

    work.add(c)

    work = corner(work, (front_wout, front_hout), overhang)
    work = corner(work, (0, front_hout), overhang)

    # tabs for top / bottom / middle plates
    r = Rectangle((0, 0), (tab_len, thick))
    r.translate(-tab_len / 2.0, -thick / 2.0)
    dx = overhang + thick
    for x in tab_locs[0]:
        c = r.copy()
        c.translate(x + dx, thick / 2.0) # bottom
        work.add(c)
        c = r.copy()
        c.translate(x + dx, front_hin + (2.5 * thick)) # top
        work.add(c)
        if back:
            c = r.copy()
            c.translate(x + dx, lo_h + (1.5 * thick)) # mid
            work.add(c)

    r = Rectangle((0, -tab_len/2.0), (thick, tab_len/2.0))
    for y in tab_locs[1]:
        # tabs into sides
        c = r.copy()
        c.translate(overhang, y + thick)
        work.add(c)
        c = r.copy()
        c.translate(front_wout - overhang - thick, y + thick)
        work.add(c)

    # nuts into sides
    nut = M3(thick)
    for y in tab_locs[2]:
        c = nut.make_plan(0)
        c.translate(overhang + (thick / 2.0), y + thick)
        work.add(c)
        c = nut.make_plan(0)
        c.translate(front_wout - overhang - (thick / 2.0), y + thick)
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
        w.translate(overhang, lo_h + thick)
        work.add(w)

    foot = make_foot(front_wout)
    work.add(foot)
    work.translate(0, feet)

    if back:
        esp = ESP().make(draw)
        esp.translate(overhang + thick, feet + thick + margin)
        work.add(esp)

    if not back:
        pir = PIR().make(draw)
        x = (front_wout - PIR.w) / 2.0
        pir.translate(x, feet + thick + thick + lo_h + margin)
        work.add(pir)

    if back:
        d1, d2, d = 3, 6, 6
        h = Hanger(r1=d1/2.0, r2=d2/2.0, d=d)
        c = h.make()
        x = front_wout / 2.0
        c.translate(x, lo_h + feet + thick + d2 + 1)
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


def make_t_holder(draw, top_h, tab_locs, is_top=False, is_mid=False, is_bot=False):
    work = Collection()

    t_holder_w = 18
    t_holder_d = tab_len * 2
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
        r += 0.4 # make the hole a bit bigger. was too tight
        d = Circle((0, 0), r)
        d.translate(t_holder_w + thick - inset, t_holder_d - inset)
        p.add_arc(d)

        d = Arc((0, 0), inset, 180, 90)
        d.translate(t_holder_w + thick - inset, t_holder_d - inset)
        p.add_arc(d)

        w.add(p)
        w.translate(front_win, top_h - t_holder_d)
        work.add(w)

    cut_locs = []

    tabs = tab_locs[0]
    for x in tabs:
        cut_locs.append((x, 0, 180))
        if not is_mid:
            cut_locs.append((x, top_h, 0))
    tabs = tab_locs[1]
    for i, y in enumerate(tabs):
        if (not is_mid) or (i == 1):
            cut_locs.append((0, y, 90))
        if not is_mid:
            cut_locs.append((front_win, y, 270))

    template = cutout(tab_len, thick)
    work = add_cutouts(work, cut_locs, template)

    if is_bot:
        c = Text((0, 0), "PIR V1.0\n(C) 2015 Dave Berkeley", height=2.0, colour=Config.engrave_colour)
        c.translate(10, 12)
        work.add(c)

    return work

#
#   Side pieces

def make_side(draw, w, h, tab_locs, is_left=False, is_right=False):
    work = Collection()

    c = Rectangle((0, 0), (w, h))
    work.add(c)

    # end tabs to interlock with horizontal plates
    cut_locs = [
        [ w / 2, 0, 180 ],
        [ w / 2, h, 0 ],
    ]
    template = cutout(w - (2 * tab_len), thick)
    work = add_cutouts(work, cut_locs, template)

    # end tabs to interlock with horizontal plates
    cut_locs = [
        #[ 0, lo_h + (thick / 2.0), 270 ],
        [ w, lo_h + (thick / 2.0), 90 ],
    ]
    template = cutout(thick, tab_len)
    work = add_cutouts(work, cut_locs, template)

    # tabs into front / back plates
    cut_locs = []
    for y in tab_locs[0]:
        cut_locs.append((0, y, 90))
        cut_locs.append((w, y, 270))
    template = cutout(tab_len, thick)
    work = add_cutouts(work, cut_locs, template)

    # Add the captive nut cutouts
    nut = M3(thick)

    locs = []
    for y in tab_locs[1]:
        locs.append((0, y, 90))
        locs.append((w, y, 270))

    for x, y, rot in locs:
        c = nut.make_elev(rot)
        c.translate(x, y)
        work = splice(work, c)

    # cable cutout on right
    if is_right:
        cable_dy = 10
        r = Temperature.cable_dia / 2.0
        c = Polygon()
        c.add(0, -r)
        c.add(-r, -r)
        c.add(-r, r)
        c.add(0, r)

        a = Arc((-r, 0), r, 90, 270)
        c.add_arc(a)
        c.translate(w, cable_dy)
        work.add(c)

    # power socket on left
    if is_left:
        c = ESP().make_elev(draw)
        c.rotate(270)
        c.translate(0, ESP.h + margin)
        work.add(c)

    work.translate(thick, thick)

    return work

#
#

def commit(work):
    move_margin(work)
    work.draw(drawing, config.cut())

config = Config()

drawing = dxf.drawing("test.dxf")

draw = False

if len(sys.argv) > 1:
    draw = True

tab_len = 6
top_h = ESP.max_d + 8
top_tab_locs = [
    [ front_win / 3.0, 2 * front_win / 3.0, ],
    [ tab_len / 2.0,  top_h - (tab_len / 2.0),  ],
]

side_h = front_hin + thick
side_tab_locs = [
    [ ESP.h / 3.0, 2 * ESP.h / 3.0, side_h - hi_h + (tab_len / 2.0), ],
    # nut locs
    [ side_h - (hi_h / 2.0), side_h - (hi_h / 2.0), ESP.h / 2.0, ESP.h / 2.0, ],
]

tab_locs = [ top_tab_locs[0], side_tab_locs[0], side_tab_locs[1] ]
work = make_front(draw, tab_locs, back=True)
commit(work)

work = make_front(draw, tab_locs)
work.translate(front_wout + spacing, 0)
commit(work)

dx = (2 * (front_wout + spacing)) + thick
dy = top_h

work = make_t_holder(draw, top_h, top_tab_locs, is_mid=True)
work.translate(dx, thick)
commit(work)

work = make_t_holder(draw, top_h, top_tab_locs, is_top=True)
work.translate(dx, dy + spacing + (1 * thick))
commit(work)

work = make_t_holder(draw, top_h, top_tab_locs, is_bot=True)
work.translate(dx, (2 * (dy + spacing)) + (3 * thick))
commit(work)

dy = front_hout + feet + spacing + top_h + (2 * thick)

work = make_side(draw, top_h, side_h, side_tab_locs, is_left=True)
work.rotate(270)
work.translate(0, dy)
commit(work)

work = make_side(draw, top_h, side_h, side_tab_locs, is_right=True)
work.rotate(270)
work.translate(front_hin + spacing + (3 * thick), dy)
commit(work)

drawing.save()

# FIN
