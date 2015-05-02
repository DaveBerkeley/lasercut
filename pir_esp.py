#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import TCut, Text, splice, cutout

# https://pypi.python.org/pypi/dxfwrite/
from dxfwrite import DXFEngine as dxf

x_margin = 10
y_margin = 20

def move_margin(work):
    work.translate(x_margin, y_margin)

#
#

thick = 3

spacing = 1

config = Config()

drawing = dxf.drawing("test.dxf")

# T-slot M3 fixings
nut = TCut(w=3, d=12-thick, shank=5, nut_w=5.5, nut_t=2.3, stress_hole=0.25)

#
#   Parts

#   ESP8266 Olimex dev board
#   https://www.olimex.com/Products/IoT/ESP8266-EVB/open-source-hardware

esp_w = 57
esp_h = 49.5
esp_dw = 49
esp_dh = 41.5
esp_pcb = 1.5
esp_hole_dia = 3 # 3.3

esp_power_h = 12.5 - esp_pcb
esp_power_x0 = 17.2
esp_power_w = 8.9
esp_solder = 3.5
esp_max_d = 16.5 - esp_pcb + esp_solder

# ESP8266 board

def make_esp(draw):
    esp = Collection()

    if draw:
        c = Rectangle((0, 0), (esp_w, esp_h))
        esp.add(c)

    in_h, in_w = (esp_h - esp_dh) / 2.0, (esp_w - esp_dw) / 2.0
    c = Circle((0, 0), esp_hole_dia / 2.0)

    d = c.copy()
    d.translate(in_w, in_h)
    esp.add(d)
    d = c.copy()
    d.translate(in_w, esp_h - in_h)
    esp.add(d)
    d = c.copy()
    d.translate(esp_w - in_w, esp_h - in_h)
    esp.add(d)
    d = c.copy()
    d.translate(esp_w - in_w, in_h)
    esp.add(d)

    return esp

#   PIR sensor
#   http://www.amazon.co.uk/dp/B00LS85XNM

pir_w = 32
pir_h = 24
pir_hole = 23
pir_fix_dia = 2
pir_fix_dx = 28

#   PIR board

def make_pir(draw):
    pir = Collection()

    if draw:
        c = Rectangle((0, 0), (pir_w, pir_h))
        pir.add(c)

    in_w = (pir_w - pir_hole) / 2.0
    in_h = (pir_h - pir_hole) / 2.0
    c = Rectangle((0, 0), (pir_hole, pir_hole))
    c.translate(in_w, in_h)
    pir.add(c)

    dh = pir_h / 2.0
    dw = (pir_w - pir_fix_dx) / 2.0
    c = Circle((0, 0), pir_fix_dia / 2.0)
    
    d = c.copy()
    d.translate(dw, dh)
    pir.add(d)

    d = c.copy()
    d.translate(pir_w - dw, dh)
    pir.add(d)

    return pir

#   Temperature sensor
#   http://www.amazon.co.uk/dp/B00CHEZ250

temp_dia = 6
temp_len = 50
temp_outer_0 = 6.5
temp_outer_1 = 4.45
temp_cable_dia = 3.9
temp_shank = 2.5

#
#   Foot

def reflect_v(poly):
    points = []
    for point in poly.points:
        points.append((-point[0], point[1]))
    poly.points = points
    def angle(a):
        if 0 <= a < 180:
            return 180 - a
        return a - 180
    for arc in poly.arcs:
        arc.x = -arc.x
        arc.start_angle = angle(arc.start_angle)
        arc.end_angle = angle(arc.end_angle)
        arc.start_angle, arc.end_angle = arc.end_angle, arc.start_angle

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
    reflect_v(d)
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

front_win = esp_w
front_hin = esp_h + pir_h

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

    foot = make_foot(front_wout)
    work.add(foot)
    work.translate(0, feet)

    if 1:
        esp = make_esp(draw)
        esp.translate(overhang + thick, feet + thick)
        work.add(esp)

    if 1:
        pir = make_pir(draw)
        x = (front_wout - pir_w) / 2.0
        pir.translate(x, feet + thick + thick + esp_h)
        work.add(pir)

    return work

#
#

draw = True

work = make_front(draw)
work.draw(drawing, config.cut())

def make_t_holder(is_top):
    work = Collection()

    top_h = esp_max_d
    t_holder_w = 18
    t_holder_d = 12
    inset = t_holder_d / 2.0

    c = Polygon()
    m = (top_h - t_holder_d) / 2.0
    c.add(front_win, top_h - m)
    c.add(front_win, top_h)
    c.add(0, top_h)
    c.add(0, 0)
    c.add(front_win, 0)
    c.add(front_win, m)
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
    y = (top_h - t_holder_d) / 2.0
    if is_top:
        r = temp_dia / 2.0
    else:
        r = temp_outer_1 / 2.0
    d = Circle((0, 0), r)
    d.translate(t_holder_w + thick - inset, t_holder_d - inset)
    p.add_arc(d)

    d = Arc((0, 0), inset, 270, 90)
    d.translate(t_holder_w + thick - inset, t_holder_d - inset)
    p.add_arc(d)

    w.add(p)
    w.translate(front_win, y)
    work.add(w)
    return work

work = make_t_holder(False)

work.translate(front_wout + spacing, 0)
work.draw(drawing, config.cut())

drawing.save()

# FIN
