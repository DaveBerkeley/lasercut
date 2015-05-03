

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import TCut

#
#   Parts

# T-slot fixings

class Nut:
    def __init__(self, w, d, shank, nut_w, nut_t, stress_hole):
        self.nut = TCut(w=w, d=d, shank=shank, nut_w=nut_w, nut_t=nut_t, stress_hole=stress_hole)

class M3:

    def __init__(self, thick, d=12):
        Nut.__init__(self, w=3, d=d-thick, shank=5, nut_w=5.5, nut_t=2.3, stress_hole=0.25)

    def make_plan(self):
        return self.nut.make_plan()

    def make_elev(self):
        return self.nut.make_elev()

#   ESP8266 Olimex dev board
#   https://www.olimex.com/Products/IoT/ESP8266-EVB/open-source-hardware

class ESP_Olimex_Dev:
    w = 57
    h = 49.5
    dw = 49
    dh = 41.5
    pcb = 1.5
    hole_dia = 3 # 3.3

    power_h = 12.5 - pcb
    power_x0 = 17.2
    power_w = 8.9
    solder = 3.5
    max_d = 16.5 - pcb + solder

    def make(self, draw):
        esp = Collection()

        if draw:
            c = Rectangle((0, 0), (self.w, self.h), colour=Config.draw_colour)
            esp.add(c)

        in_h, in_w = (self.h - self.dh) / 2.0, (self.w - self.dw) / 2.0
        c = Circle((0, 0), self.hole_dia / 2.0)

        d = c.copy()
        d.translate(in_w, in_h)
        esp.add(d)
        d = c.copy()
        d.translate(in_w, self.h - in_h)
        esp.add(d)
        d = c.copy()
        d.translate(self.w - in_w, self.h - in_h)
        esp.add(d)
        d = c.copy()
        d.translate(self.w - in_w, in_h)
        esp.add(d)

        return esp

#   PIR sensor
#   http://www.amazon.co.uk/dp/B00LS85XNM

class PIR_DYPME003:
    w = 32
    h = 24
    hole = 23
    fix_dia = 2
    fix_dx = 28

    def make(self, draw):
        pir = Collection()

        if draw:
            c = Rectangle((0, 0), (self.w, self.h), colour=Config.draw_colour)
            pir.add(c)

        in_w = (self.w - self.hole) / 2.0
        in_h = (self.h - self.hole) / 2.0
        c = Rectangle((0, 0), (self.hole, self.hole))
        c.translate(in_w, in_h)
        pir.add(c)

        dh = self.h / 2.0
        dw = (self.w - self.fix_dx) / 2.0
        c = Circle((0, 0), self.fix_dia / 2.0)
        
        d = c.copy()
        d.translate(dw, dh)
        pir.add(d)

        d = c.copy()
        d.translate(self.w - dw, dh)
        pir.add(d)

        return pir

#   Temperature sensor
#   http://www.amazon.co.uk/dp/B00CHEZ250

class Temperature_DS18b20:
    dia = 6
    length = 50
    outer_0 = 6.5
    outer_1 = 4.45
    cable_dia = 3.9
    shank = 2.5

# FIN
