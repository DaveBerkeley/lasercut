#!/usr/bin/python

import math

try:
    import sdxf
except:
    print "Need library from", "http://pypi.python.org/pypi/SDXF" 
    raise

#    drawing.append(sdxf.Line(line_2))
#
#    # draw the last arc section to the tip of the next tooth
#    arc2 = sdxf.Arc(center=(x2,y2,0), radius=outer_curve_radius,
#            endAngle=next_angle, 
#            startAngle=math.degrees(a2_1))
#    drawing.append(arc2)

#
#

def opto(x, y, inner_radius, outer_radius, vanes, hole_dia):

    line = sdxf.Circle(center=(x, y), radius=hole_dia / 2.0)
    drawing.append(line)

    for vane in range(vanes):
        def xy(x, y, r, a):
            return x + (r * math.cos(a)), y + (r * math.sin(a))

        a0, a1 = [ (i * 360.0 / vanes) for i in [ vane, vane+1] ] 
        r0, r1 = [ math.radians(i) for i in [ a0, a1 ] ] 
        if (vane & 0x01): # odd vanes are blank
            line = sdxf.Arc(center=(x,y), radius=inner_radius,
                    startAngle=a0, endAngle=a1)
            drawing.append(line)
            continue

        points = [ 
            xy(x, y, outer_radius, r0),
            xy(x, y, inner_radius, r0),
        ]
        line = sdxf.PolyLine(points)
        drawing.append(line)

        points = [
            xy(x, y, inner_radius, r1),
            xy(x, y, outer_radius, r1),
        ]
        line = sdxf.PolyLine(points)
        drawing.append(line)

        line = sdxf.Arc(center=(x,y), radius=outer_radius, 
                startAngle=a0, endAngle=a1)
        drawing.append(line)

#

inner_radius = 5
outer_radius = 13
vanes = 36
hole_dia = 3.0

margin = 10
A4 = 210, 297
A4 = [ (i - margin) for i in A4 ]

drawing = sdxf.Drawing()

vanes = 4

step = outer_radius * 2
for x in range(0, A4[0] - step, step):
    for y in range(0, A4[1] - step, step):
        opto(x, y, inner_radius, outer_radius, vanes, hole_dia)
        vanes += 2
    break

PATH = 'opto.dxf'
print "Writing", PATH
drawing.saveas(PATH)

# FIN
