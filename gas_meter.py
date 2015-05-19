#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Circle, Collection, Config
from laser import corner
from render import DXF as dxf

#
#

# Surround dimensions
w_inner = 94.0
h_inner = 50.1
edge = 8.0
hole_r = 3 / 2.0
w_outer, h_outer = w_inner+(2*edge), h_inner+(2*edge)

# Plate dimensions
plate_h = h_inner + (2.0 * edge)
plate_w = 35.0
sensor_from_edge = 16.0
plate_dx = edge + (w_inner - sensor_from_edge) - (plate_w/2.0)

# corner supports
support_w = 15.0

# PCB dimensions
board_h = 35.0
board_w = 30.0
board_dx = (plate_w - board_w) / 2.0
board_dy = edge + ((h_inner - board_h) / 2.0) # mid
mouse_w = 5.0
mouse_h = 5.0
mouse_dx = (board_w - mouse_w) / 2.0
mouse_dy = (board_h - mouse_h) / 2.0
led_r = 2.0
led_dx = mouse_dx + (mouse_w / 2.0)
led_dy = mouse_dy + mouse_h + 3

#
#

def make_board(draw):
    work = Collection()

    r = Rectangle((0, 0), (board_w, board_h), colour=Config.draw_colour)
    if draw:
        work.add(r)

    # fixing holes
    inset = 3.0
    for point in r.points[:-1]:
        x, y = point
        def fn(a):
            if a:
                return a - inset
            return a + inset
        x, y = fn(x), fn(y)
        c = Circle((x, y), hole_r)
        work.add(c)

    # hole for the camera
    r = Rectangle((0, 0), (mouse_w, mouse_h))
    r.translate(mouse_dx, mouse_dy)
    work.add(r)

    # hole for the LED
    c = Circle((0, 0), led_r)
    c.translate(led_dx, led_dy)
    work.add(c)

    return work

def make_face(draw):
    work = Collection()

    inset = edge / 2.0
    r = Rectangle((0, 0), (w_outer, h_outer))
    work.add(r)

    r = Rectangle((0, 0), (w_inner, h_inner))
    r.translate(edge, edge)
    work.add(r)

    # round the corners
    work = corner(work, (0, 0), edge)
    work = corner(work, (w_outer, 0), edge)
    work = corner(work, (0, h_outer), edge)
    work = corner(work, (w_outer, h_outer), edge)

    # fixing holes for the plate
    dy = edge / 2.0
    dx = plate_dx
    xy = [
        (dx+inset, dy), 
        (dx+plate_w-inset, dy), 
        (dx+inset, h_outer-dy), 
        (dx+plate_w-inset, h_outer-dy),
    ]
    for x, y in xy:
        c = Circle((x, y), hole_r)
        work.add(c)

    # fixing holes for the corners
    c = Circle((support_w+(edge/2), h_outer-(edge/2)), hole_r)
    work.add(c)
    c = Circle((edge/2, h_outer-edge-support_w+(edge/2)), hole_r)
    work.add(c)
    c = Circle((support_w+edge-(edge/2), (edge/2)), hole_r)
    work.add(c)
    c = Circle((edge/2, support_w+edge-(edge/2)), hole_r)
    work.add(c)

    if draw:
        # meter digits (approx position)
        digit_w, digit_h, digit_dx = 7.0, 10.0, 10.0
        r = Rectangle((0, 0), (digit_w, digit_h), colour=Config.draw_colour)
        dx, dy = 10 + edge, 30.0
        for i in range(4):
            d = r.copy()
            d.translate(dx, dy)
            dx += digit_dx
            work.add(d)

    info = {}
    info["surround"] = work

    # make the plate
    r = Rectangle((0, 0), (plate_w, plate_h))
    for p in r.points[:-1]:
        def fn(a):
            if a:
                return a - inset
            return a + inset
        x, y = p
        x, y = fn(x), fn(y)
        c = Circle((x, y), hole_r)
        r.add_arc(c)

    # add the board to the plate
    work = Collection(r)
    p = make_board(draw)
    p.translate(board_dx, board_dy)
    work.add(p)

    info["plate"] = work

    work = Polygon()
    work.add(0, 0)
    work.add(0, support_w+edge) # corner
    work.add(support_w+edge, support_w+edge)
    work.add(support_w+edge, support_w)
    work.add(edge, 0)
    work.close()
    work = corner(work, (0, support_w+edge), edge)

    c = Circle((support_w+(edge/2), support_w+(edge/2)), hole_r)
    work.add(c)
    c = Circle((edge/2, edge/2), hole_r)
    work.add(c)

    info["corner"] = work

    return info

#
#

if __name__ == "__main__":
    config = Config()

    draw = len(sys.argv) > 1

    drawing = dxf.drawing("test.dxf")

    info = make_face(draw)

    if draw:
        work = Collection()
        p = info["plate"]
        p.translate(plate_dx, 0)
        work.add(p)

        p = info["surround"]
        work.add(p)

        p = info["corner"].copy()
        p.translate(0, h_outer-edge-support_w)
        work.add(p)

        p = info["corner"].copy()
        p.rotate(90)
        p.translate(edge+support_w, 0)
        work.add(p)
    else:
        spacing = 1.0
        work = Collection()
        p = info["plate"]
        p.rotate(-90)
        dy = plate_w+edge+spacing
        p.translate(edge+spacing, dy)
        work.add(p)

        p = info["surround"]
        work.add(p)

        p = info["corner"].copy()
        dy = edge + spacing
        dx = edge+(2*spacing)+plate_h
        p.translate(dx, dy)
        work.add(p)

        p = info["corner"].copy()
        dy += edge + support_w + spacing
        p.translate(dx, dy)
        work.add(p)

    work.draw(drawing, config.cut())

    drawing.save()

# FIN
