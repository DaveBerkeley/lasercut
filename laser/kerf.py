#!/usr/bin/python

from laser import Config, Polygon, Rectangle, Circle, Collection
from laser import angle, radians, degrees, rotate_2d, parallel_intersect
from render import DXF as dxf

from gears import make_involute

#
#   Compensate for kerf

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
