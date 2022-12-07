import sdl2
import sdl2.sdlgfx

import math
import ctypes

from ..igraphlet import *
from ..movable import *

from ...graphics.image import *
from ...graphics.colorspace import *

###################################################################################################
class IShapelet(IGraphlet, IMovable):
    def __init__(self, color = -1, border_color = -1):
        super(IShapelet, self).__init__()
        self.enable_resizing(True)
        self.__last_pos = (math.nan, math.nan)
        self.__color = color
        self.__border_color = border_color
            
# public
    def draw(self, renderer, flx, fly, flWidth, flHeight):
        x, y = round(flx), round(fly)
        width, height = round(flWidth), round(flHeight)
        
        if self.__last_pos[0] != flx or (self.__last_pos[1]) != fly:
            self.__last_pos = (flx, fly)
            self._on_moved(flx, fly)
        
        if self.__color >= 0:
            r, g, b = RGB_FromHexadecimal(self.__color)
            self._fill_shape(renderer, x, y, width, height, r, g, b, 0xFF)

        if self.__border_color >= 0:
            r, g, b = RGB_FromHexadecimal(self.__border_color)
            self._draw_shape(renderer, x, y, width, height, r, g, b, 0xFF)
                
# public
    def set_color(self, color):
        if self.__color != color:
            self.__color = color
            self.notify_updated()

    def get_color(self):
        return self.__color

    def set_border_color(self, color):
        if self.__border_color != color:
            self.__border_color = color
            self.notify_updated()
    
    def get_border_color(self):
        return self.__border_color

    def get_shape_origin(self):
        return 0.0, 0.0

# protected
    def _on_moved(self, new_x, new_y): pass
    def _draw_shape(self, renderer, x, y, width, height, r, g, b, a): pass
    def _fill_shape(self, renderer, x, y, width, height, r, g, b, a): pass

# protected
    def _dirty_cached_position(self):
        self.__last_pos = (math.nan, math.nan)

###################################################################################################
class Linelet(IShapelet):
    def __init__(self, ex, ey, color):
        super(Linelet, self).__init__(color, -1)
        self.__epx = ex
        self.__epy = ey
        
    def get_extent(self, x, y):
        return abs(self.__epx), abs(self.__epy)

    def _on_resize(self, w, h, width, height):
        self.__epx *= w / width
        self.__epy *= h / height

    def _fill_shape(self, renderer, x, y, width, height, r, g, b, a):
        xn, yn = round(self.__epx), round(self.__epy)

        if xn < 0:
            x = x - xn
        
        if yn < 0:
            y = y - yn

        sdl2.sdlgfx.aalineRGBA(renderer, x, y, x + xn, y + yn, r, g, b, a)        

class HLinelet(Linelet):
    def __init__(self, width, color):
        super(HLinelet, self).__init__(width, 0.0, color)

class VLinelet(Linelet):
    def __init__(self, height, color):
        super(VLinelet, self).__init__(0.0, height, color)

###################################################################################################
class Rectanglet(IShapelet):
    def __init__(self, width, height, color, border_color = -1):
        super(Rectanglet, self).__init__(color, border_color)
        self.__width, self.__height = width, height

    def get_extent(self, x, y):
        return self.__width, self.__height

    def _on_resize(self, w, h, width, height):
        self.__width = w
        self.__height = h
    
    def _draw_shape(self, renderer, x, y, width, height, r, g, b, a):
        sdl2.sdlgfx.rectangleRGBA(renderer, x + width, y, x, y + height, r, g, b, a)

    def _fill_shape(self, renderer, x, y, width, height, r, g, b, a):
        sdl2.sdlgfx.boxRGBA(renderer, x + width, y, x, y + height, r, g, b, a)

class Squarelet(Rectanglet):
    def __init__(self, edge_size, color, border_color=-1):
        super(Squarelet, self).__init__(edge_size, edge_size, color, border_color)

class RoundedRectanglet(IShapelet):
    def __init__(self, width, height, radius, color, border_color = -1):
        super(RoundedRectanglet, self).__init__(color, border_color)
        self.__width, self.__height = width, height
        self.__radius = radius

    def get_extent(self, x, y):
        return self.__width, self.__height

    def _on_resize(self, w, h, width, height):
        self.__width = w
        self.__height = h
    
    def _draw_shape(self, renderer, x, y, width, height, r, g, b, a):
        rad = self.__radius

        if rad < 0.0:
            rad = -min(self.__width, self.__height) * rad

        sdl2.sdlgfx.roundedRectangleRGBA(renderer, x + width, y, x, y + height, round(rad), r, g, b, a)

    def _fill_shape(self, renderer, x, y, width, height, r, g, b, a):
        rad = self.__radius

        if rad < 0.0:
            rad = -min(self.__width, self.__height) * rad

        sdl2.sdlgfx.roundedBoxRGBA(renderer, x + width, y, x, y + height, round(rad), r, g, b, a)

class RoundedSquarelet(RoundedRectanglet):
    def __init__(self, edge_size, radius, color, border_color = -1):
        super(RoundedSquarelet, self).__init__(edge_size, edge_size, radius, color, border_color)

class Ellipselet(IShapelet):
    def __init__(self, aradius, bradius, color, border_color = -1):
        super(Ellipselet, self).__init__(color, border_color)
        self.__aradius, self.__bradius = aradius, bradius

    def get_extent(self, x, y):
        return self.__aradius * 2.0, self.__bradius * 2.0

    def _on_resize(self, w, h, width, height):
        self.__aradius = w * 0.5
        self.__bradius = h * 0.5
    
    def _draw_shape(self, renderer, x, y, width, height, r, g, b, a):
        rx = round(self.__aradius) - 1
        ry = round(self.__bradius) - 1
        cx = rx + x
        cy = ry + y

        if rx == ry:
            sdl2.sdlgfx.aacircleRGBA(renderer, cx, cy, rx, r, g, b, a)
        else:
            sdl2.sdlgfx.aaellipseRGBA(renderer, cx, cy, rx, ry, r, g, b, a)

    def _fill_shape(self, renderer, x, y, width, height, r, g, b, a):
        rx = round(self.__aradius) - 1
        ry = round(self.__bradius) - 1
        cx = rx + x
        cy = ry + y

        if rx == ry:
            sdl2.sdlgfx.filledCircleRGBA(renderer, cx, cy, rx, r, g, b, a)
            sdl2.sdlgfx.aacircleRGBA(renderer, cx, cy, rx, r, g, b, a)
        else:
            sdl2.sdlgfx.filledEllipseRGBA(renderer, cx, cy, rx, ry, r, g, b, a)
            sdl2.sdlgfx.aaellipseRGBA(renderer, cx, cy, rx, ry, r, g, b, a)

class Circlet(Ellipselet):
    def __init__(self, radius, color, border_color = -1):
        super(Circlet, self).__init__(radius, radius, color, border_color)

###################################################################################################
class RegularPolygonlet(IShapelet):
    def __init__(self, n, radius, color, border_color = -1, rotation = 0.0):
        super(RegularPolygonlet, self).__init__(color, border_color)
        self.__PTArray = ctypes.c_int16 * n
        self.__n = n
        self.__aradius, self.__bradius = radius, radius
        self.__rotation = rotation
        self.__lx, self.__rx, self.__ty, self.__by = 0.0, 0.0, 0.0, 0.0
        self.__pts = []
        self.__xs = self.__PTArray()
        self.__ys = self.__PTArray()
        self.__initialize_vertice()

    def get_extent(self, x, y):
        return self.__rx - self.__lx + 1, self.__by - self.__ty + 1
    
    def _on_resize(self, w, h, width, height):
        self.__aradius = w / width
        self.__bradius = h / height
        self.__initialize_vertice()

    def _on_moved(self, new_x, new_y):
        xoff = new_x - self.__lx
        yoff = new_y - self.__ty

        for idx in range(0, self.__n):
            pt = self.__pts[idx]

            self.__xs[idx] = round(pt[0] + xoff)
            self.__ys[idx] = round(pt[1] + yoff)

    def _draw_shape(self, renderer, x, y, width, height, r, g, b, a):
        sdl2.sdlgfx.aapolygonRGBA(renderer, self.__xs, self.__ys, self.__n, r, g, b, a)
    
    def _fill_shape(self, renderer, x, y, width, height, r, g, b, a):
        sdl2.sdlgfx.filledPolygonRGBA(renderer, self.__xs, self.__ys, self.__n, r, g, b, a)
        sdl2.sdlgfx.aapolygonRGBA(renderer, self.__xs, self.__ys, self.__n, r, g, b, a)
    
    def __initialize_vertice(self):
        start = math.radians(self.__rotation)
        delta = 2.0 * math.pi / float(self.__n)

        self.__lx = self.__aradius
        self.__ty = self.__bradius
        self.__rx = -self.__lx
        self.__by = -self.__ty

        self.__pts.clear()

        for idx in range(0, self.__n):
            theta = start + delta * float(idx)
            this_x = round(self.__aradius * math.cos(theta))
            this_y = round(self.__bradius * math.sin(theta))
            
            self.__pts.append((this_x, this_y))

            if self.__rx < this_x:
                self.__rx = this_x
            elif self.__lx > this_x:
                self.__lx = this_x

            if self.__by < this_y:
                self.__by = this_y
            elif self.__ty > this_y:
                self.__ty = this_y
