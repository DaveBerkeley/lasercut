#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Circle, Collection, Config
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
esp_max = 16.5 - esp_pcb
esp_solder = 3.5

#   Temperature sensor
#   http://www.amazon.co.uk/dp/B00CHEZ250

temp_dia = 6
temp_len = 50
temp_outer_0 = 6.5
temp_outer_1 = 4.45
temp_cable_dia = 3.9
temp_shank = 2.5

#   PIR sensor
#   http://www.amazon.co.uk/dp/B00LS85XNM

pir_w = 32
pir_h = 24
pir_hole = 23
pir_fix_dia = 2
pir_fix_dx = 28

#
#

feet = 3
overhang = 3

front_win = esp_w
front_hin = esp_h + pir_h

front_hout = front_hin + (2 * thick) + (2 * overhang) # + feet
front_wout = front_win + (2 * thick) + (2 * overhang)

work = Collection()

c = Rectangle((0, 0), (front_wout, front_hout))
work.add(c)

# ESP8266 board

def make_esp():
    esp = Collection()
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

#   PIR board

def make_pir():
    pir = Collection()

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

#
#

if 0:
    esp = make_esp()
    esp.translate(overhang + thick, overhang + thick)
    work.add(esp)

pir = make_pir()
work.add(pir)

work.draw(drawing, config.cut())

drawing.save()

# FIN
