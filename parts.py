

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import TCut

#
#   Parts

# T-slot fixings

class Nut:
    def __init__(self, w, d, shank, nut_w, nut_t, stress_hole):
        self.nut = TCut(w=w, d=d, shank=shank, nut_w=nut_w, nut_t=nut_t, stress_hole=stress_hole)

    def make_plan(self, orient):
        return self.nut.make_plan((0, 0), orient)

    def make_elev(self, orient):
        return self.nut.make_elev((0, 0), orient)

class M3(Nut):
    def __init__(self, thick, d=12):
        Nut.__init__(self, w=3, d=d-thick, shank=5, nut_w=5.5, nut_t=2.3, stress_hole=0.25)

#   ESP8266 Olimex dev board
#   https://www.olimex.com/Products/IoT/ESP8266-EVB/open-source-hardware

class ESP_Olimex_Dev:
    w = 57.4
    h = 49.6
    dw = 49.35
    dh = 41.6
    pcb = 1.5
    hole_dia = 3 # 3.3

    power_h = 12.5 - pcb
    power_x0 = 17.5
    power_w = 9.0
    solder = 3.7
    max_d = 16.8 - pcb + solder

    def make(self, draw):
        esp = Collection()

        if draw:
            c = Rectangle((0, 0), (self.w, self.h), colour=Config.draw_colour)
            esp.add(c)
            c = Rectangle((0, 0), (self.power_w, self.power_w), colour=Config.draw_colour)
            c.translate(0, self.power_x0 - self.power_w)
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

    def make_elev(self, draw):
        work = Collection()
        if draw:
            c = Rectangle((0, 0), (self.h, self.max_d), colour=Config.draw_colour)
            work.add(c)
            c = Rectangle((0, 0), (self.h, self.pcb), colour=Config.draw_colour)
            c.translate(0, self.solder)
            work.add(c)

        c = Rectangle((0, 0), (self.power_w, self.power_h))
        c.translate(self.h - self.power_x0, self.pcb + self.solder)
        work.add(c)
        return work

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
            c = Circle((0, 0), self.hole / 2.0, colour=Config.draw_colour)
            c.translate(self.w/2.0, self.h/2.0)
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
    dia = 6.1
    length = 50
    outer_0 = 6.5
    outer_1 = 4.7
    cable_dia = 3.8
    shank = 2.5

#
#

class Hanger:

    def __init__(self, r1=3, r2=5, d=8):
        self.r1 = r1
        self.r2 = r2
        self.d = d

    def make(self):
        w = Collection()
        c = Arc((0, 0), self.r1, 0, 180)
        c.translate(0, self.d)
        w.add(c)
        c = Circle((0, 0), self.r2)
        w.add(c)
        d = self.r1
        c = Polygon()
        c.add(-d, 0)
        c.add(-d, self.d)
        w.add(c)
        c = Polygon()
        c.add(d, 0)
        c.add(d, self.d)
        w.add(c)
        return w

# FIN
