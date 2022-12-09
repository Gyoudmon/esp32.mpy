import math

###############################################################################
class MatterAnchor(object):
    LT = 0x4983917e165afce8
    CT = 0x45469ade8ed1ff0e
    RT = 0x43fa3ada0199d0ed
    LC = 0x45be256177a1bacb
    CC = 0x4d3b7e0e5d4bf118
    RC = 0x4a89be34d21896a6
    LB = 0x49071ea39c89fc24
    CB = 0x40774aafb4b0d0ae
    RB = 0x4208392ecc81b775

class BorderEdge(object):
    TOP = 0x4d52cf9d2eeb506f
    RIGHT = 0x488d2013b5d8f2ad
    BOTTOM = 0x463b469498d6f36a
    LEFT = 0x45c62f50ae7e873d
    NONE = 0x4151ac35cfedfb3d

class BorderStrategy(object):
    IGNORE = 0x402f7a5172c81a41
    STOP = 0x407c35437235f05f
    BOUNCE = 0x4fcc175c111c2d94

###############################################################################
class IMatterInfo(object):
    def __init__(self, master):
        self.master = master

class IMatter(object):
    def __init__(self):
        super(IMatter, self).__init__()
        self.info = None
        self.__resizable, self.__resize_anchor = False, MatterAnchor.LT
        self.__anchor, self.__anchor_x, self.__anchor_y = MatterAnchor.LT, 0.0, 0.0
        self.__deal_with_events = False
        self.__findable = True

    def __del__(self):
        self.info = None
        
    def pre_construct(self): pass
    def post_construct(self): pass

    def master(self):
        plane = None

        if self.info:
            plane = self.info.master

        return plane

# public
    def construct(self): pass
    def get_extent(self, x, y): return 0.0, 0.0
    def get_margin(self, x, y): return 0.0, 0.0, 0.0, 0.0
    def update(self, count, interval, uptime): pass
    def draw(self, ledscr, X, Y, Width, Height): pass
    def ready(self): return True

# public
    def enable_events(self, yes_or_no, low_level = False):
        self.__deal_with_events = yes_or_no
    
    def enable_resizing(self, yes_no, anchor = MatterAnchor.CC):
        self.__resizable = yes_no
        self.__resize_anchor = anchor

    def resizable(self):
        return self.__resizable, self.__resize_anchor

    def events_allowed(self):
        return self.__deal_with_events

# public
    def get_location(self, anchor = MatterAnchor.LT):
        sx = 0.0
        sy = 0.0

        if self.info:
            sx, sy = self.info.master.get_matter_location(self, anchor)

        return sx, sy

    def moor(self, anchor):
        if anchor != MatterAnchor.LT:
            if self.info:
                self.__anchor = anchor
                self.__anchor_x, self.__anchor_y = self.info.master.get_matter_location(self)

    def clear_moor(self):
        self.__anchor = MatterAnchor.LT
    
    def notify_updated(self):
        if self.info:
            if self.__anchor != MatterAnchor.LT:
                self.info.master.move_to(self, self.__anchor_x, self.__anchor_y, self.__anchor)
                self.clear_moor()
            
            self.info.master.notify_updated()

    def resize(self, w, h):
        if self.__resizable:
            if w > 0.0 and h > 0.0:
                x, y = self.get_location(MatterAnchor.LT)
                width, height = self.get_extent(x, y)

                if width != w or height != h:
                    self.moor(self.__resize_anchor)
                    self._on_resize(w, h, width, height)
                    self.notify_updated()

    def camouflage(self, yes_or_no):
        self.__findable = yes_or_no
    
    def concealled(self):
        return not self.__findable
 
# proteceted
    def _on_resized(self, width, height, old_width, old_height):
        pass

################################################################################################### 
class IMovable(IMatter):
    def __init__(self):
        super(IMovable, self).__init__()

        self.__border_strategies = {}
        self.set_border_strategy(BorderStrategy.IGNORE)
        self.__xspeed = 0.0
        self.__yspeed = 0.0

# public
    def on_border(self, hoffset, voffset):
        hstrategy = BorderStrategy.IGNORE
        vstrategy = BorderStrategy.IGNORE

        if hoffset < 0.0:
            hstrategy = self.__border_strategies[BorderEdge.LEFT]
        elif hoffset > 0.0:
            hstrategy = self.__border_strategies[BorderEdge.RIGHT]

        if voffset < 0.0:
            vstrategy = self.__border_strategies[BorderEdge.TOP]
        elif voffset > 0.0:
            vstrategy = self.__border_strategies[BorderEdge.BOTTOM]

        if hstrategy == BorderStrategy.STOP or vstrategy == BorderStrategy.STOP:
            self.__xspeed = 0.0
            self.__yspeed = 0.0
        else:
            if hstrategy == BorderStrategy.BOUNCE:
                self.__xspeed *= -1.0

            if vstrategy == BorderStrategy.BOUNCE:
                self.__yspeed *= -1.0

    def set_border_strategy(self, strategy):
        if isinstance(strategy, int):
            self.__set_border_strategy(strategy, strategy, strategy, strategy)
        else:
            c = len(strategy)

            if c == 2:
                self.__set_border_strategy(strategy[0], strategy[1], strategy[0], strategy[1])
            else:
                self.__set_border_strategy(strategy[0], strategy[1], strategy[2], strategy[3])
    
# public
    def set_speed(self, speed, degree):
        rad = math.radians(degree)

        self.__xspeed = speed * math.cos(rad)
        self.__yspeed = speed * math.sin(rad)

    def x_speed(self):
        return self.__xspeed

    def y_speed(self):
        return self.__yspeed

# public
    def motion_stop(self, horizon, vertical):
        if horizon:
            self.__xspeed = 0.0

        if vertical:
            self.__yspeed = 0.0

    def motion_bounce(self, horizon, vertical):
        if horizon:
            self.__xspeed *= -1.0

        if vertical:
            self.__yspeed *= -1.0

#private
    def __set_border_strategy(self, ts, rs, bs, ls):
        self.__border_strategies[BorderEdge.TOP] = ts
        self.__border_strategies[BorderEdge.RIGHT] = rs
        self.__border_strategies[BorderEdge.BOTTOM] = bs
        self.__border_strategies[BorderEdge.LEFT] = ls

###################################################################################################
class IShapelet(IMovable):
    def __init__(self, filled, c = 1):
        super(IShapelet, self).__init__()
        self.enable_resizing(True)
        self._dirty_cached_position()
        self.__filled = filled
        self.__c = c
            
# public
    def draw(self, ledscr, flx, fly, flWidth, flHeight):
        x, y = round(flx), round(fly)
        width, height = round(flWidth), round(flHeight)
        
        if self.__last_pos[0] != flx or (self.__last_pos[1]) != fly:
            self.__last_pos = (flx, fly)
            self._on_moved(flx, fly)
        
        if self.__filled:
            self._fill_shape(ledscr, x, y, width, height, self.__c)
        else:
            self._draw_shape(ledscr, x, y, width, height, self.__c)
                
# public
    def set_filled(self, filled):
        if self.__filled != filled:
            self.__filled = filled
            self.notify_updated()

    def is_filled(self):
        return self.__filled

    def set_draw_mode(self, c):
        if self.__c != c:
            self.__c = c
            self.notify_updated()
    
    def get_draw_mode(self):
        return self.__c

# protected
    def _on_moved(self, new_x, new_y): pass
    def _draw_shape(self, ledscr, x, y, width, height, c): pass
    def _fill_shape(self, ledscr, x, y, width, height, c): pass

# protected
    def _dirty_cached_position(self):
        # mpython doesn't have `math.nan`
        self.__last_pos = (False, False)

###################################################################################################
class Linelet(IShapelet):
    def __init__(self, ex, ey, c = 1):
        super(Linelet, self).__init__(True, c)
        self.__epx = ex
        self.__epy = ey
        
    def get_extent(self, x, y):
        return abs(self.__epx), abs(self.__epy)

    def _on_resize(self, w, h, width, height):
        self.__epx *= w / width
        self.__epy *= h / height

    def _fill_shape(self, ledscr, x, y, width, height, c):
        xn, yn = round(self.__epx), round(self.__epy)

        if xn < 0:
            x = x - xn
        
        if yn < 0:
            y = y - yn

        ledscr.line(x, y, x + xn, y + yn, c)

class HLinelet(Linelet):
    def __init__(self, width, color):
        super(HLinelet, self).__init__(width, 0.0, color)

class VLinelet(Linelet):
    def __init__(self, height, color):
        super(VLinelet, self).__init__(0.0, height, color)

###################################################################################################
class Rectanglet(IShapelet):
    def __init__(self, width, height, filled = True, c = 1):
        super(Rectanglet, self).__init__(filled, c)
        self.__width, self.__height = width, height

    def get_extent(self, x, y):
        return self.__width, self.__height

    def _on_resize(self, w, h, width, height):
        self.__width = w
        self.__height = h
    
    def _draw_shape(self, ledscr, x, y, width, height, c):
        ledscr.rect(x, y, width, height, c)

    def _fill_shape(self, ledscr, x, y, width, height, c):
        ledscr.fill_rect(x, y, width, height, c)

class Squarelet(Rectanglet):
    def __init__(self, edge_size, filled, c = 1):
        super(Squarelet, self).__init__(edge_size, edge_size, filled, c)

class Trianglet(IShapelet):
    def __init__(self, x2, y2, x3, y3, filled, c = 1):
        super(Trianglet, self).__init__(filled, c)
        self.__x2, self.__y2 = x2, y2
        self.__x3, self.__y3 = x3, y3

    def get_extent(self, x, y):
        xmin = min(0.0, self.__x2, self.__x3)
        ymin = min(0.0, self.__y2, self.__y3)
        xmax = max(0.0, self.__x2, self.__x3)
        ymax = max(0.0, self.__y2, self.__y3)

        return xmax - xmin + 1.0, ymax - ymin + 1.0

    def _on_resize(self, w, h, width, height):
        xratio = w / width
        yratio = h / height

        self.__x2 *= xratio
        self.__y2 *= yratio
        self.__x3 *= xratio
        self.__y3 *= yratio

    def _draw_shape(self, ledscr, x, y, width, height, c):
        x -= round(min(0.0, self.__x2, self.__x3))
        y -= round(min(0.0, self.__y2, self.__y3))
        x2 = round(self.__x2) + x
        y2 = round(self.__y2) + y
        x3 = round(self.__x3) + x
        y3 = round(self.__y3) + y

        ledscr.triangle(x, y, x2, y2, x3, y3, c)

    def _fill_shape(self, ledscr, x, y, width, height, c):
        x -= round(min(0.0, self.__x2, self.__x3))
        y -= round(min(0.0, self.__y2, self.__y3))
        x2 = round(self.__x2) + x
        y2 = round(self.__y2) + y
        x3 = round(self.__x3) + x
        y3 = round(self.__y3) + y

        ledscr.fill_triangle(x, y, x2, y2, x3, y3, c)

class Circlet(IShapelet):
    def __init__(self, radius, filled, c = 1):
        super(Circlet, self).__init__(filled, c)
        self.__radius = radius

    def get_extent(self, x, y):
        return self.__radius * 2.0, self.__radius * 2.0

    def _on_resize(self, w, h, width, height):
        self.__radius = min(w, h) * 0.5
    
    def _draw_shape(self, ledscr, x, y, width, height, c):
        r = round(self.__radius) - 1
        ledscr.circle(x + r, y + r, r, c)

    def _fill_shape(self, ledscr, x, y, width, height, c):
        r = round(self.__radius) - 1
        ledscr.fill_circle(x + r, y + r, r, c)
