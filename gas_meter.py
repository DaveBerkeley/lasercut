#!/usr/bin/python

import sys

from laser import Rectangle, Polygon, Circle, Collection, Config
from laser import corner
from render import DXF as dxf

#
#

# 0.1 inch pin spacing
pin_spacing = 2.54

# Surround dimensions
w_inner = 94.0
h_inner = 50.1
edge = 9.0
hole_r = 3 / 2.0
w_outer, h_outer = w_inner+(2*edge), h_inner+(2*edge)
dial_r = 10.0
dial_dy = 25.0 # from bot of face
dial_dx = 16.0 # from rh edge

# Nano dimensions
nano_w = 17.9
nano_h = 43.3

# other d
board_edge_w = pin_spacing
board_edge_h = 2 * pin_spacing
# ADNS2610 chip
chip_body = 9.1
chip_w = 12.85
chip_h = 9.9
chip_r = 5.6 / 2
chip_dy = chip_h - 4.45
chip_mag = 1.8 # make the hole this much bigger than the sensor opening

# meter digits (approx position)
digit_w, digit_h, digit_dx = 7.0, 10.0, 9.0

# Plate dimensions
plate_h = h_inner + (2.0 * edge)

# PCB dimensions
board_h = plate_h
board_w = nano_w + chip_w + (3 * board_edge_w) + (3 * pin_spacing)

plate_w = board_w

# corner supports
support_w = 12.0

board_dx = (plate_w - board_w) / 2.0
board_dy = edge + ((h_inner - board_h) / 2.0) # mid
mouse_w = 5.0
mouse_h = 5.0
mouse_dx = (board_w - mouse_w) / 2.0
mouse_dy = (board_h - mouse_h) / 2.0
led_r = 5 / 2.0
led_dy = 3 * pin_spacing # above centre of sensor
led_dy2 = 3 * pin_spacing # below centre of sensor
led_dx = 2 * pin_spacing

#
#

def nearest_01_inch(x):
    x /= pin_spacing
    x += 0.5
    x = int(x)
    x *= pin_spacing
    return x
#
#

def make_chip(draw):
    work = Collection()
    c = Circle((chip_w/2.0, chip_dy), chip_r, colour=Config.draw_colour)
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

    # make 0.1 inch grid
    if draw:
        i = 0
        while i < board_w:
            j = 0
            while j < board_h:
                c = Circle((i, j), 0.05, colour=Config.draw_colour)
                work.add(c)
                j += pin_spacing
            i += pin_spacing

    if draw:
        r = Rectangle((0, 0), (nano_w, nano_h), colour=Config.draw_colour)
        r.translate(board_edge_w * 1, pin_spacing * 5)
        work.add(r)

    if 1:
        # add corner holes

        x0 = 2 * pin_spacing
        x1 = nearest_01_inch(board_w - (2 * pin_spacing))
        y0 = x0
        y1 = nearest_01_inch(board_h - (2 * pin_spacing))
        holes = [
            (x0, y0), (x1, y0), (x0, y1), (x1, y1),
        ]

        for x, y in holes:
            c = Circle((x, y), hole_r)
            work.add(c)

    # add the chip so it's chip_dy optical centre aligns with the dial centre
    chip = make_chip(draw)
    dy = edge + dial_dy - board_dy - chip_dy
    chip.translate((board_edge_w * 2) + nano_w, dy)
    work.add(chip)

    sensor = chip.info["sensor"]
    c = Circle((sensor.x, sensor.y), chip_r * chip_mag)
    work.add(c)

    # holes for the LEDs
    c = Circle((sensor.x + led_dx, sensor.y + led_dy), led_r)
    work.add(c)
    c = Circle((sensor.x - led_dx, sensor.y + led_dy), led_r)
    work.add(c)
    c = Circle((sensor.x + led_dx, sensor.y - led_dy2), led_r)
    work.add(c)
    c = Circle((sensor.x - led_dx, sensor.y - led_dy2), led_r)
    work.add(c)

    work.info = { 
        "sensor" : (sensor.x, sensor.y),
        "board"  : (board_w, board_h),
        "holes"  : holes,
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

    d = sdx + dial_dx # d = from board left edge to inner right edge
    dx = edge + (w_inner - d)
    work.info["board_dx"] = dx

    # fixing holes for the plate
    if 1:
        holes = board.info["holes"]
        for x, y in holes:
            c = Circle((x+dx, y), hole_r)
            work.add(c)

    # fixing holes for the corner supports
    e = edge / 2.0
    c = Circle((support_w+e, h_outer-e), hole_r)
    work.add(c)
    c = Circle((e, h_outer-edge-support_w+e), hole_r)
    work.add(c)
    c = Circle((support_w+edge-e, e), hole_r)
    work.add(c)
    c = Circle((e, support_w+edge-e), hole_r)
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

    work = Collection()
    r = Rectangle((0, 0), (plate_w, plate_h))

    # add the board to the plate
    work.add(r)
    p = make_board(draw)
    p.translate(board_dx, board_dy)
    work.add(p)

    info["plate"] = work

    # make the corner supports
    work = Rectangle((0, 0), (support_w+edge, support_w+edge))
    work = corner(work, (support_w+edge, 0), edge)
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

    layout = len(sys.argv) > 1
    if layout:
        eng = sys.argv[1] == "eng"
        if eng:
            layout = False
    else:
        eng = False

    drawing = dxf.drawing("test.dxf")

    info = make_face(layout or eng)

    if layout:
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

    work.translate(10, 20) # for printing
    work.draw(drawing, config.cut())

    drawing.save()

# FIN
