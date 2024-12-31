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
chamfer = 6
centre_r = 10
hole_r = 3

class Rete(SCAD):
    
    def __init__(self, filename, config):
        super().__init__(filename)
        self.config = config

        from astrolabe import r_eq, r_can
        self.rad_capricorn = config.size
        self.rad_equator = r_eq(self.rad_capricorn)
        self.rad_cancer = r_can(self.rad_equator)
        print(self.rad_capricorn, self.rad_equator, self.rad_cancer, file=sys.stderr)

        print("$fn = 100;", file=self.f)

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
                #self.xform("translate", v=[ 0, 0, -0.01, ])
                #self.cylinder(h=(disc_thick*2)+0.02, r1=r-outer_disc_w)
    
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
 
    def stars(self):
        for name in brightest:
            star = stars.star(name)
            star.compute()
            print(name, star.a_ra, star.a_dec, float(star.a_ra), float(star.a_dec), star.mag, file=sys.stderr)

    def draw(self):

        outer_cut_angle = 30

        with Union(self):
            with Difference(self):
                with Union(self):
                    # outer disc
                    self.comment("outer disc")
                    self.xform("linear_extrude", height=disc_thick)
                    with Difference(self):
                        # outer disc
                        radius = self.rad_capricorn
                        self.circle(r=radius)
                        self.circle(r=radius-outer_disc_w)
                        a = radians(outer_cut_angle)
                        d = radius / math.tan(a)
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
                        self.xform("linear_extrude", height=disc_thick)
                        self.function("square", size=[w, d], center=True)

                #self.xform("#translate", v = [ 0, 0, 0 ] )
                self.ecliptic_cut()

            # centre hole
            self.xform("linear_extrude", height=disc_thick)
            with Difference(self):
                self.circle(r=centre_r)
                self.circle(r=hole_r)

            self.ecliptic()

            self.stars()

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

    "Polaris",
]

if __name__ == "__main__":
    rete = Rete()
    rete.draw()

#   FIN
