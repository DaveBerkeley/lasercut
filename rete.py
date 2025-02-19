#!/usr/bin/env python3

import sys
import cmath
import math

import ephem # pyephem
import ephem.stars as stars

from laser.render import Difference, Union, Intersection, SCAD
from laser.laser import radians, degrees

#radius = 80
outer_disc_w = 10
disc_thick = 1
chamfer = 4
centre_surround = 4

class Rete(SCAD):
 
    def __init__(self, filename, config):
        super().__init__(filename)
        self.config = config

        from astrolabe import r_eq, r_can, r_dec
        self.rad_capricorn = config.size/2
        self.rad_equator = r_eq(self.rad_capricorn)
        self.rad_cancer = r_can(self.rad_equator)
        print(self.rad_capricorn, self.rad_equator, self.rad_cancer, file=sys.stderr)

        print("$fn = 100;", file=self.f)
        self.r_dec = r_dec

    def circle(self, r=None):
        self.function("circle", r=r)

    def ticks(self, r, length, step, size):
        print("TODO", "ticks", file=sys.stderr)
        return
        for angle in range(0, 360, step):
            z = cmath.rect(r, radians(angle))
            zz = z * (0-1j)
            #print(angle, z, zz, file=sys.stderr)

            self.xform("translate", v=[ z.real, z.imag, 0, ])
            self.xform("rotate", a=[ zz.real, zz.imag, 0, ])
            self.cylinder(h=length, r1=size)

    def ecliptic(self):
        # Ecliptic

        x0 = self.rad_capricorn
        x1 = -self.rad_cancer
        x = (x0 + x1) / 2.0
        r = (x0 - x1) / 2.0
        self.xform("translate", v=[ x, 0, 0, ])
        with Union(self):
            with Difference(self):
                with Union(self):
                    self.cylinder(h=disc_thick, r1=r)
                    self.xform("translate", v=[ 0, 0, disc_thick-0.01, ])
                    self.cylinder(h=disc_thick, r1=r, r2=r-chamfer)
                self.xform("translate", v=[ 0, 0, -0.01, ])
                self.cylinder(h=(disc_thick*2)+0.02, r1=r-outer_disc_w)
    
                self.xform("translate", v=[ 0, 0, disc_thick-0.01, ])
                with Union(self):
                    self.ticks(r, chamfer*2, 30, 0.75)
                    self.ticks(r, chamfer*2, 5, 0.5)

    def ecliptic_cut(self):
        self.comment("ecliptic_cut")

        x0 = self.rad_capricorn
        x1 = -self.rad_cancer
        x = (x0 + x1) / 2.0
        r = (x0 - x1) / 2.0
        self.xform("translate", v=[ x, 0, -0.01, ])
        self.cylinder(h=(disc_thick*2)+0.02, r1=r-outer_disc_w)
 
    def star_mount(self, name, d, angle):
        w = self.rad_equator / 10
        self.xform("rotate", a=angle)
        self.xform("linear_extrude", height=disc_thick*2)
        with Union(self):
            points = [
                [ 0, 0 ],
                [ w, w/2 ],
                [ d, w/2 ],
                [ d, -w/2 ],
                [ w, -w/2 ],
                [ 0, 0 ],
            ]
            self.function("polygon", points=points)

    def star(self, name, star):

        skip = [
            "Polaris",
            "Dubhe",
            "Sirius",
            "Mirzam",
            "Castor",
            "Pollux",
            "Elnath",
            "Alcaid",
            "Alnilam",
            "Alnitak",
        ]
        if name in skip:
            return

        stars = {
            "Regulus" : (170, "Reg.", 0.1),
            "Altair" : (0, None, 0.5),
            "Procyon" : (0, None, 0.5),
            "Vega" : (180, None, 0.5),
            "Deneb" : (180, None, 0.35),
            "Arcturus" : (0, None, 0.4),
            "Mirfak" : (25, None, 0.2),
            "Aldebaran" : (180, None, 0.2),
            "Alhena" : (180, None, 0.2),
            "Alioth" : (260, None, 0.2),
            "Alkaid" : (260, None, 0.2),
            "Betelgeuse" : (0, None, 0.6),
            "Bellatrix" : (15, None, 0.5),
            "Menkalinan" : (0, None, 0.15),
            "Capella" : (0, None, 0.15),
        }

        setting = stars.get(name) or (0, name, 0.2)

        #print(name, float(star.a_ra), float(star.a_dec), star.mag, file=sys.stderr)
        r = self.r_dec(self.rad_equator, degrees(star.a_dec))
        if r > self.rad_capricorn:
            return

        #if not name in stars:
        #    print("no entry for", name, file=sys.stderr)
        #    return

        a = float(star.a_ra) + radians(90)
        print(name, r, a, star.mag)
        z = cmath.rect(r, a)
        #self.xform("scale", v= [ 1, 1, 3 ])
        self.xform("translate", v= [ z.real, z.imag, 0 ])
        with Union(self):
            rot = setting[0] + degrees(a)
            self.star_mount(name, self.rad_equator * setting[2], rot)
            self.xform("translate", v= [ 0, 0, 2 ])
            self.text(text=setting[1] or name, height=3, rotation=rot)
 
    def stars(self):
        #for name in brightest:
        for name in stars.stars.keys():
            try:
                star = stars.star(name)
            except KeyError:
                raise Exception(name, stars.stars.keys())
            star.compute()
            if star.mag > 2.0:
                continue # too dim
            self.star(name, star)

    def draw(self):

        outer_cut_angle = 30
        a = radians(outer_cut_angle)
        radius = self.rad_capricorn
        d = radius / math.tan(a)

        with Difference(self):
            with Union(self):
                with Difference(self):
                    with Union(self):
                        # outer disc
                        self.comment("outer disc")
                        self.xform("linear_extrude", height=disc_thick*2)
                        with Difference(self):
                            # outer disc
                            self.circle(r=radius)
                            self.circle(r=radius-outer_disc_w)
                            points = [
                                [ 0, 0 ],
                                [ radius, -d ],
                                [ radius, d ],
                            ]
                            self.function("polygon", points=points)

                        # connecting bar to ecliptic
                        self.comment("connecting bar to ecliptic")
                        w = outer_disc_w
                        d = self.rad_capricorn
                        for a in [ outer_cut_angle+180, -outer_cut_angle ]:
                            self.xform("rotate", a=a )
                            self.xform("translate", v = [ 0, d/2, 0 ] )
                            self.xform("linear_extrude", height=disc_thick*2)
                            self.function("square", size=[w, d], center=True)

                    #self.xform("#translate", v = [ 0, 0, 0 ] )
                    self.ecliptic_cut()

                # connecting outer ring, centre, ecliptic
                self.xform("translate", v = [ -w/2, 0, 0 ] )
                self.xform("linear_extrude", height=disc_thick*2)
                self.function("square", size=[w, d*2 - 1], center=True)

                self.ecliptic()
                self.stars()

                # centre mount
                self.xform("linear_extrude", height=disc_thick*2)
                self.circle(r=centre_surround + self.config.hole)

            # centre hole
            self.xform("translate", v = [ 0, 0, -0.01 ] )
            self.xform("linear_extrude", height=disc_thick*2 + 0.02)
            self.circle(r=self.config.hole)


brightest = [
    # http://astropixels.com/stars/brightstars.html
    "Sirius",
    "Canopus",
    "Rigil Kentaurus",
    "Arcturus",
    "Vega",
    "Capella",
    "Rigel",
    "Procyon",
    "Betelgeuse",
    "Achernar",
    "Hadar",
    "Altair",
    "Acrux",
    "Aldebaran",
    "Spica",
    "Antares",

    "Menkar",
    "Rasalhague",
    "Alphard",
    #"Enif",

    "Polaris",
]

if __name__ == "__main__":
    rete = Rete()
    rete.draw()

#   FIN
