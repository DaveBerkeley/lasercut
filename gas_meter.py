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
edge = 9.0
hole_r = 3 / 2.0
w_outer, h_outer = w_inner+(2*edge), h_inner+(2*edge)
dial_r = 10.0
dial_dy = 25.0 # from bot of face
dial_dx = 16.0 # from rh edge

# meter digits (approx position)
digit_w, digit_h, digit_dx = 7.0, 10.0, 9.0

# Plate dimensions
plate_h = h_inner + (2.0 * edge)

#
#

def make_board(draw):
    work = Collection()

    # data from Gerber files for PCB
    sensor_x, sensor_y = 32.385, 24.638 
    board_w, board_h = 48.26, 45.72
    holes = [
        (10.16, 40.64),
        (10.16, 5.08),
        (43.18, 40.64),
        (43.18, 5.08),
    ]

    r = Rectangle((0, 0), (board_w, board_h), colour=Config.draw_colour)
    if draw:
        work.add(r)

    for x, y in holes:
        c = Circle((x, y), hole_r)
        work.add(c)

    if draw:
        c = Circle((sensor_x, sensor_y), 5.6/2, colour=Config.draw_colour)
        work.add(c)

    work.info = { 
        "sensor" : (sensor_x, sensor_y),
        "board"  : (board_w, board_h),
        "holes"  : holes,
    }

    return work

#
# PCB dimensions
w = make_board(True)
b = w.info["board"]
board_w, board_h = b

plate_w = board_w

# corner supports
support_w = 12.0

board_dx = (plate_w - board_w) / 2.0
board_dy = edge + ((h_inner - board_h) / 2.0) # mid

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
    e = edge / 2.0
    plate_holes = [
        (e, e),
        (plate_w - e, e),
        (plate_w - e, plate_h - e),
        (e, plate_h - e),
    ]
    for x, y in plate_holes:
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
        c = Circle((x, y), 3.5, colour=Config.draw_colour)
        work.add(c)

    info = {}
    info["surround"] = work

    # make the plate

    work = Collection()
    r = Rectangle((0, 0), (plate_w, plate_h))

    # add the board to the plate
    work.add(r)
    p = make_board(draw)
    dup = edge + (dial_dy - sdy)
    p.translate(board_dx, dup)
    work.add(p)

    # add fixing holes
    for x, y in plate_holes:
        c = Circle((x, y), hole_r)
        work.add(c)

    # cut a big hole for the camera and LEDs
    c = Circle((sdx, dup + sdy), dial_r)
    work.add(c)

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
