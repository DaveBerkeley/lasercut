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


drawing.save()

# FIN
