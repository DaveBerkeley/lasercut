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
dial_r = 10.0
dial_dy = 25.0 # from bot of face
dial_dx = 16.0 # from rh edge

# Nano dimensions
nano_w = 17.9
nano_h = 43.3
# other d
board_edge_w = 3
board_edge_h = 5
# ADNS2610 chip
chip_body = 9.1
chip_w = 12.85
chip_h = 9.9
chip_r = 5.6 / 2
chip_dy = chip_h - 4.45

# meter digits (approx position)
digit_w, digit_h, digit_dx = 7.0, 10.0, 9.0

# PCB dimensions
board_h = nano_h + (2 * board_edge_h)
board_w = nano_w + chip_w + (3 * board_edge_w)

# Plate dimensions
plate_h = h_inner + (2.0 * edge)
plate_w = board_w

# corner supports
support_w = 15.0

board_dx = (plate_w - board_w) / 2.0
board_dy = edge + ((h_inner - board_h) / 2.0) # mid
mouse_w = 5.0
mouse_h = 5.0
mouse_dx = (board_w - mouse_w) / 2.0
mouse_dy = (board_h - mouse_h) / 2.0
led_r = 2.0
led_dy = 7.0 # above centre of sensor

#
#

def make_chip(draw):
    work = Collection()
    c = Circle((chip_w/2.0, chip_dy), chip_r)
    work.add(c)
    work.info = { "sensor" : c }
    if draw:
        r = Rectangle((0, 0), (chip_w, chip_h), colour=Config.draw_colour)
        work.add(r)
        r = Rectangle((0, 0), (chip_body, chip_h), colour=Config.draw_colour)
        r.translate((chip_w - chip_body) / 2.0, 0)
        work.add(r)
    return work

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

    if draw:
        r = Rectangle((0, 0), (nano_w, nano_h), colour=Config.draw_colour)
        r.translate(board_edge_w, board_edge_h)
        work.add(r)

    # add the chip so it's chip_dy optical centre aligns with the dial centre
    chip = make_chip(draw)
    dy = edge + dial_dy - board_dy - chip_dy
    chip.translate((board_edge_w * 2) + nano_w, dy)
    work.add(chip)

    sensor = chip.info["sensor"]
    c = Circle((sensor.x, sensor.y), chip_r * 1.5)
    work.add(c)

    # hole for the LED
    c = Circle((sensor.x, sensor.y + led_dy), led_r)
    work.add(c)

    work.info = { 
        "sensor" : (sensor.x, sensor.y),
        "board"  : (board_w, board_h),
    }
    return work

#
#

def make_face(draw):
    work = Collection()
    work.info = {}

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

    board = make_board(draw)
    sdx, sdy = board.info["sensor"]
    work.info.update(board.info)

    # fixing holes for the plate
    dy = edge / 2.0
    d = sdx + dial_dx # d = from board left edge to inner right edge
    dx = edge + (w_inner - d)
    work.info["board_dx"] = dx
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
        # show meter digits
        r = Rectangle((0, 0), (digit_w, digit_h), colour=Config.draw_colour)
        dx, dy = 10 + edge, 30.0
        for i in range(4):
            d = r.copy()
            d.translate(dx, dy)
            dx += digit_dx
            work.add(d)

    # show the position of the dial
    if draw:
        x, y = edge + w_inner - dial_dx, edge + dial_dy
        c = Circle((x, y), dial_r, colour=Config.draw_colour)
        work.add(c)
        c = Circle((x, y), 3.0, colour=Config.draw_colour)
        work.add(c)

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

    # make the corner supports

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

        p = info["surround"]
        plate_dx = p.info["board_dx"]
        work.add(p)

        p = info["plate"]
        p.translate(plate_dx, 0)
        work.add(p)

        p = info["corner"].copy()
        p.translate(0, h_outer-edge-support_w)
        work.add(p)

        p = info["corner"].copy()
        p.rotate(90)
        p.translate(edge+support_w, 0)
        work.add(p)

        work.translate(10, 20) # for printing
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
