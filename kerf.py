#!/usr/bin/python

from laser import Config, Polygon, Rectangle, Circle, Collection
from laser import angle, radians, degrees, rotate_2d
from render import DXF as dxf

from gears import make_involute

#
#   Compensate for kerf

def parallel(points, d, inner):
    x0, y0 = points[0]
    x1, y1 = points[1]
    dx, dy = x1 - x0, y1 - y0
    a = angle(dx, dy)
    # vector at 90 degrees to line
    if inner:
        x, y = rotate_2d(a, 0, d)
    else:
        x, y = rotate_2d(a, 0, -d)
    return (x0 + x, y0 + y), (x1 + x, y1 + y)

def vertical(xy0, xy1):
    x0, _ = xy0
    x1, _ = xy1
    return x1 == x0

def equation_of_line(xy0, xy1):
    x0, y0 = xy0
    x1, y1 = xy1
    dx, dy = x1 - x0, y1 - y0
    m = (y1 - y0) / (x1 - x0)
    return m, y0 - (m * x0) 

def intersect(e0, e1):
    # given 2 equations of line
    # calculate intersection point
    m0, c0 = e0
    m1, c1 = e1
    x = (c0 - c1) / (m1 - m0)
    y = (m0 * x) + c0
    return x, y

def solve_for_x(x, xy):
    m, b = equation_of_line(*xy)
    y = (x * m) + b
    return x, y

def parallel_intersect(xy0, xy1, d, inner):
    xy0 = parallel(xy0, d, inner)
    xy1 = parallel(xy1, d, inner)
    if vertical(*xy0):
        # solve for x = x0
        return solve_for_x(xy0[1][0], xy1)
    elif vertical(*xy1):
        # solve for x = x1
        return solve_for_x(xy1[0][0], xy0)
    else:
        e0, e1 = equation_of_line(*xy0), equation_of_line(*xy1)
        return intersect(e0, e1)

#
#

def line_pairs(points):
    first = None
    while len(points) >= 3:
        l0 = points[:2]
        l1 = points[1:3]
        yield l0, l1
        points = points[1:]
        if first is None:
            first = l0
    # and the first shall be last
    yield points, first

def dekerf(poly, kerf, inner, **kwargs):
    # assert closed Polygon
    assert isinstance(poly, Polygon)
    assert poly.points[0] == poly.points[-1]
    work = Polygon(**kwargs)

    # offset by half the kerf width
    kerf /= 2.0

    for xy0, xy1 in line_pairs(poly.points[:]):
        x, y = parallel_intersect(xy0, xy1, kerf, inner)
        work.add(x, y)
    work.close()

    # compensate for arcs, taking account of the 'hole' status
    for arc in poly.arcs:
        a = arc.copy()
        if a.hole:
            a.radius -= kerf
        else:
            a.radius += kerf
        work.add_arc(a)

    if hasattr(poly, "info"):
        work.info = poly.info

    return work

#
#

if __name__ == "__main__":

    def commit(work):
        work.draw(drawing, config.cut())

    config = Config()

    drawing = dxf.drawing("test.dxf")

    N = 20
    PA = 14.5
    pitch_dia = 20

    work = make_involute(pitch_dia, N, PA)
    c = Circle((0, 0), 4)
    work.add_arc(c)
    c = Circle((0, 0), 2, hole=False)
    work.add_arc(c)
    commit(work)

    kerf = 0.5
    work = dekerf(work.copy(), kerf, False, colour=12)
    commit(work)

    drawing.save()

# FIN
