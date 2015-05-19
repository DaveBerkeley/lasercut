#!/usr/bin/python

from laser import Rectangle, Polygon, Circle, Arc, Collection, Config
from laser import radians, degrees, angle, rotate_2d, splice, corner
from render import DXF as dxf

#
#

w_inner = 200
h_inner = 150
edge = 10
hole_r = 3 / 2.0
plate_h = h_inner + (2 * edge)
plate_w = 50
plate_dx = 140

board_h = 40
board_w = 45
board_dx = (plate_w - board_w) / 2.0
board_dy = 60
mouse_w = 5
mouse_h = 5
mouse_dx = (board_w - mouse_w) / 2.0
mouse_dy = (board_h - mouse_h) / 2.0

def make_board(draw):
    work = Collection()

    r = Rectangle((0, 0), (board_w, board_h), colour=Config.draw_colour)
    if draw:
        work.add(r)

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

    r = Rectangle((0, 0), (mouse_w, mouse_h))
    r.translate(mouse_dx, mouse_dy)
    work.add(r)

    return work

def make_face(draw):
    work = Collection()

    w_outer, h_outer = w_inner+(2*edge), h_inner+(2*edge)
    r = Rectangle((0, 0), (w_outer, h_outer))
    work.add(r)

    r = Rectangle((0, 0), (w_inner, h_inner))
    r.translate(edge, edge)
    work.add(r)

    rad = 10
    work = corner(work, (0, 0), rad)
    work = corner(work, (w_outer, 0), rad)
    work = corner(work, (0, h_outer), rad)
    work = corner(work, (w_outer, h_outer), rad)

    info = {}
    info["surround"] = work

    r = Rectangle((0, 0), (plate_w, plate_h))
    inset = edge / 2.0
    for p in r.points[:-1]:
        def fn(a):
            if a:
                return a - inset
            return a + inset
        x, y = p
        x, y = fn(x), fn(y)
        c = Circle((x, y), hole_r)
        r.add_arc(c)
    info["plate"] = r

    info["board"] = make_board(draw)

    return info

#
#

if __name__ == "__main__":
    config = Config()
    draw = True

    drawing = dxf.drawing("test.dxf")

    info = make_face(draw)

    work = Collection()
    p = info["surround"]
    work.add(p)

    p = info["plate"]
    p.translate(plate_dx, 0)
    work.add(p)

    p = info["board"]
    p.translate(plate_dx, 0)
    p.translate(board_dx, board_dy)
    work.add(p)

    work.draw(drawing, config.cut())

    drawing.save()

# FIN
