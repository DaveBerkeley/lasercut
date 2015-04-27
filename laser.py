
# https://pypi.python.org/pypi/SDXF
import sdxf

#
#

class Material:

    def __init__(self, w, h, t):
        self.width = w
        self.height = h
        self.thickness = t

#
#

class Config:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

#
#

class TCut:

    def __init__(self, config, nut_size, nut_length):
        self.config = config
        self.nut_size = nut_size
        self.nut_length = nut_length

    def set_drawing(self, drawing):
        self.drawing = drawing

    def draw_elev(self, x, y):
        pass

    def draw_plan(self, x, y):
        pass

# FIN
