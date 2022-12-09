# MindPlus with microPython

from universe import *
from matter import *

###############################################################################
class Cosmos(Universe):
    def __init__(self, fps = 24, background = None, width = 128, height = 64):
        super(Cosmos, self).__init__(fps, background, width, height)
        self.__mleft, self.__mtop, self.__mright, self.__mbottom = 0.0, 0.0, 0.0, 0.0
        self.__head_matter = None
        self.__translate_x, self.__translate_y = 0.0, 0.0
        self.__scale_x, self.__scale_y = 1.0, 1.0
        self.size_cache_invalid()
        
    def __del__(self):
        self.__head_matter = None
        self.size_cache_invalid()

# public
    def load(self, Width, Height): pass
    
    def reflow(self, width, height): pass
    
    def update(self, interval, count, uptime):
        pass

    def draw(self, ledscr, X, Y, Width, Height):
        dsX, dsY = max(0.0, X), max(0.0, Y)
        dsWidth, dsHeight = X + Width, Y + Height

        if self.__head_matter:
            child = self.__head_matter

            while True:
                info = child.info
                mwidth, mheight = child.get_extent(info.x, info.y)

                mx = (info.x + self.__translate_x) * self.__scale_x + X
                my = (info.y + self.__translate_y) * self.__scale_y + Y

                if rectangle_overlay(mx, my, mx + mwidth, my + mheight, dsX, dsY, dsWidth, dsHeight):
                    child.draw(ledscr, mx, my, mwidth, mheight)

                child = info.next
                if child == self.__head_matter:
                    break
    
    def can_exit(self): return False

# public
    def find_matter(self, x, y):
        found = None

        if self.__head_matter:
            head_info = self.__head_matter.info
            child = head_info.prev

            while True:
                info = child.info

                if not child.concealled():
                    sx, sy, sw, sh = _unsafe_get_matter_bound(child, info)

                    sx += (self.__translate_x * self.__scale_x)
                    sy += (self.__translate_y * self.__scale_y)

                    if flin(sx, x, sx + sw) and flin(sy, y, sy + sh):
                        if child.is_colliding_with_mouse(x - sx, y - sy):
                            found = child
                            break

                child = info.prev

                if child == head_info.prev:
                    break

        return found

    def get_matter_location(self, m, anchor):
        info = _cosmos_matter_info(self, m)
        x, y = False, 0.0

        if info:
            sx, sy, sw, sh = _unsafe_get_matter_bound(m, info)
            fx, fy = _matter_anchor_fraction(anchor)
            x = sx + sw * fx
            y = sy + sh * fy

        return x, y

    def get_matter_boundary(self, m):
        info = _cosmos_matter_info(self, m)
        x, y, width, height = False, 0.0, 0.0, 0.0
        
        if info:
            x, y, width, height = _unsafe_get_matter_bound(m, info)

        return x, y, width, height

    def get_matters_boundary(self):
        self.__recalculate_matters_extent_when_invalid()

        w = self.__mright - self.__mleft
        h = self.__mbottom - self.__mtop

        return self.__mleft, self.__mtop, w, h

    def insert(self, m, x = 0.0, y = 0.0, anchor = MatterAnchor.LT, dx = 0.0, dy = 0.0):
        if m.info is None:
            fx, fy = _matter_anchor_fraction(anchor)
            
            info = _bind_matter_owership(self, m)
            if not self.__head_matter:
                self.__head_matter = m
                info.prev = self.__head_matter
            else:
                head_info = self.__head_matter.info
                prev_info = head_info.prev.info

                info.prev = head_info.prev
                prev_info.next = m
                head_info.prev = m
            info.next = self.__head_matter

            self.begin_update_sequence()
            m.pre_construct()
            m.construct()
            m.post_construct()
            _unsafe_move_matter_via_info(self, m, info, x, y, fx, fy, dx, dy)
            
            if m.ready():
                if self.__scale_x != 1.0 or self.__scale_y != 1.0:
                    _do_resize(self, m, info, self.__scale_x, self.__scale_y)

                self.notify_updated()
                self.on_matter_ready(m)
            else:
                self.notify_updated()
            
            self.end_update_sequence()

        return m

    def move(self, m, x, y):
        info = _cosmos_matter_info(self, m)

        if info:
            if _unsafe_do_moving_via_info(self, info, x, y, False):
                self.notify_updated()
        elif self.__head_matter:
            child = self.__head_matter

            while True:
                info = child.info

                if info.selected:
                    _unsafe_do_moving_via_info(self, info, x, y, False)

                child = info.next
                if child == self.__head_matter:
                    break
            
            self.notify_update()
    
    def move_to(self, matter, target, anchor = MatterAnchor.LT, dx = 0.0, dy = 0.0):
        '''
        Move the game object to the target position, aligned by the anchor

        :param matter: the game object
        :param target: the target position, which can be shaped as one of
                            (x, y)
                            (target_matter, target_anchor)
                            (target_matter, target_x_fraction, target_y_fraction)
                            (target_matter_for_x, x_fraction, target_matter_for_y, y_fraction)
        :param anchor: the aligning anchor of the game object, which can be shaped as one of
                            anchor
                            (width_fraction, height_fraction)
        :param dx: the final translation of x
        :param dy: the final translation of y
        '''

        info = _cosmos_matter_info(self, matter)
        x, y = False, False
        
        if info:
            target_shape = len(target)
            
            if target_shape == 2:
                if isinstance(target[0], IMatter):
                    tinfo = _cosmos_matter_info(self, target[0])

                    if tinfo:
                        tx, ty, tw, th = _unsafe_get_matter_bound(target[0], tinfo)
                        tfx, tfy = _matter_anchor_fraction(target[1])
                        x = tx + tw * tfx
                        y = ty + th * tfy
                else:
                    x, y = target[0], target[1]
            elif target_shape == 3:
                tinfo = _cosmos_matter_info(self, target[0])

                if tinfo:
                    tx, ty, tw, th = _unsafe_get_matter_bound(target[0], tinfo)
                    x = tx + tw * target[1]
                    y = ty + th * target[2]
            else:
                xinfo = _cosmos_matter_info(self, target[0])
                yinfo = _cosmos_matter_info(self, target[2])

                if xinfo and yinfo:
                    xtx, _, xtw, _ = _unsafe_get_matter_bound(target[0], xinfo)
                    _, yty, _, yth = _unsafe_get_matter_bound(target[2], yinfo)
                    x = xtx + xtw * target[1]
                    y = yty + yth * target[2]

        if x and y:
            fx, fy = _matter_anchor_fraction(anchor)
            
            if _unsafe_move_matter_via_info(self, matter, info, x, y, fx, fy, dx, dy):
                self.notify_updated()
    
    def remove(self, m):
        info = _cosmos_matter_info(self, m)

        if info:
            prev_info = info.prev
            next_info = info.next

            prev_info.next = info.next
            next_info.prev = info.prev

            if self.__head_matter == m:
                if self.__head_matter == info.next:
                    self.__head_matter = None
                else:
                    self.__head_matter = info.next

            if self.__hovering_matter == m:
                self.__hovering_matter = None
            
            self.notify_updated()
            self.size_cache_invalid()
    
    def erase(self):
        self.__head_matter = None
        self.size_cache_invalid()

    def size_cache_invalid(self):
        self.__mright = self.__mleft - 1.0

# protected
    def _on_big_bang(self, width, height):
        self.load(width, height)

    def _on_elapse(self, interval, count, uptime):
        self.begin_update_sequence()
        self.__on_elapse(count, interval, uptime)
        self.update(count, interval, uptime)
        self.end_update_sequence()
    
    def notify_matter_ready(self, m):
        info = _cosmos_matter_info(self, m)

        if info:
            if info.iasync:
                self.size_cache_invalid()
                self.begin_update_sequence()

                _unsafe_move_async_matter_when_ready(self, m, info)

                self.notify_updated()
                self.on_matter_ready(m)
                self.end_update_sequence()

    def on_matter_ready(self, m): pass

# private
    def __recalculate_matters_extent_when_invalid(self):
        if self.__mright < self.__mleft:
            if self.__head_matter:
                child = self.__head_matter
                self.__mleft, self.__mtop = math.inf, math.inf
                self.__mright, self.__mbottom = -math.inf, -math.inf

                while True:
                    info = child.info

                    x, y, w, h = _unsafe_get_matter_bound(child, info)
                    self.__mleft = min(self.__mleft, x)
                    self.__mright = max(self.__mright, x + w)
                    self.__mtop = min(self.__mtop, y)
                    self.__mbottom = max(self.__mbottom, y + h)

                    child = info.next
                    if child == self.__head_matter:
                        break
            else:
                self.__mleft, self.__mtop = 0.0, 0.0
                self.__mright, self.__mbottom = 0.0, 0.0

    def __on_elapse(self, count, interval, uptime):
        if self.__head_matter:
            child = self.__head_matter

            while True:
                dwidth, dheight = self.get_extent()
                info = child.info
                
                child.update(count, interval, uptime)

                if isinstance(child, IMovable):
                    xspd, yspd = child.x_speed(), child.y_speed()
                    hdist, vdist = 0.0, 0.0

                    if xspd != 0.0 or yspd != 0.0:
                        info.x += xspd
                        info.y += yspd

                        cwidth, cheight = child.get_extent(info.x, info.y)
                            
                        if info.x < 0:
                            hdist = info.x
                        elif info.x + cwidth > dwidth:
                            hdist = info.x + cwidth - dwidth

                        if info.y < 0:
                            vdist = info.y
                        elif info.y + cheight > dheight:
                            vdist = info.y + cheight - dheight

                        if hdist != 0.0 or vdist != 0.0:
                            child.on_border(hdist, vdist)
                            xspd = child.x_speed()
                            yspd = child.y_speed()

                            if xspd == 0.0 or yspd == 0.0:
                                if info.x < 0.0:
                                    info.x = 0.0
                                elif info.x + cwidth > dwidth:
                                    info.x = dwidth - cwidth

                                if info.y < 0.0:
                                    info.y = 0.0
                                elif info.y + cheight > dheight:
                                    info.y = dheight - cheight

                        self.notify_updated()
                
                child = info.next

                if child == self.__head_matter:
                    break

###################################################################################################
class _MatterInfo(IMatterInfo):
    def __init__(self, master):
        super(_MatterInfo, self).__init__(master)
        
        self.x, self.y = 0.0, 0.0
        self.selected = False
        self.iasync = None
        
        self.next, self.prev = None, None

def _bind_matter_owership(master, m):
    m.info = _MatterInfo(master)
    
    return m.info

def _cosmos_matter_info(master, m):
    info = None

    if m.info and m.info.master == master:
        info = m.info
    
    return info

def _unsafe_get_matter_bound(m, info):
    width, height = m.get_extent(info.x, info.y)

    return info.x, info.y, width, height

def _matter_anchor_fraction(a):
    fx, fy = 0.0, 0.0

    if isinstance(a, int): 
        if a == MatterAnchor.LT: pass
        elif a == MatterAnchor.LC: fy = 0.5
        elif a == MatterAnchor.LB: fy = 1.0
        elif a == MatterAnchor.CT: fx = 0.5          
        elif a == MatterAnchor.CC: fx, fy = 0.5, 0.5
        elif a == MatterAnchor.CB: fx, fy = 0.5, 1.0
        elif a == MatterAnchor.RT: fx = 1.0
        elif a == MatterAnchor.RC: fx, fy = 1.0, 0.5
        elif a == MatterAnchor.RB: fx, fy = 1.0, 1.0
    else:
        fx, fy = a[0], a[1]

    return fx, fy

def _unsafe_do_moving_via_info(master, info, x, y, absolute):
    moved = False

    if not absolute:
        x += info.x
        y += info.y

    if info.x != x or info.y != y:
        info.x = x
        info.y = y

        master.size_cache_invalid()
        moved = True

    return moved

def _unsafe_move_matter_via_info(master, m, info, x, y, fx, fy, dx, dy):
    ax, ay = 0.0, 0.0

    if m.ready():
        sx, sy, sw, sh = _unsafe_get_matter_bound(m, info)
        ax = sw * fx
        ay = sh * fy
    else:
        info.iasync = {}
        info.iasync['x0'] = x
        info.iasync['y0'] = y
        info.iasync['fx0'] = fx
        info.iasync['fy0'] = fy
        info.iasync['dx0'] = dx
        info.iasync['dy0'] = dy

    return _unsafe_do_moving_via_info(master, info, x - ax + dx, y - ay + dy, True)

def _unsafe_move_async_matter_when_ready(master, m, info):
    asi = info.iasync
    info.iasync = None

    return _unsafe_move_matter_via_info(master, m, info, asi['x0'], asi['y0'], asi['fx0'], asi['fy0'], asi['dx0'], asi['dy0'])

def _do_resize(master, m, info, scale_x, scale_y, prev_scale_x = 1.0, prev_scale_y = 1.0):
    resizable, resize_anchor = m.resizable()

    if resizable:
        sx, sy, sw, sh = _unsafe_get_matter_bound(m, info)
        fx, fy = _matter_anchor_fraction(resize_anchor)

        m.resize(sw / prev_scale_x * scale_x, sh / prev_scale_y * scale_y)
        nw, nh = m.get_extent(sx, sy)

        nx = sx + (sw - nw) * fx
        ny = sy + (sh - nh) * fy

        _unsafe_do_moving_via_info(master, info, nx, ny, True)

# Physics
###################################################################################################
def flin(dmin, datum, dmax):
    return dmin <= datum and datum <= dmax

###################################################################################################
def point_inside(px, py, x1, y1, x2, y2):
    if x1 <= x2:
        x_okay = flin(x1, px, x2)
    else:
        x_okay = flin(x2, px, x1)

    if y1 <= y2:
        y_okay = flin(y1, px, y2)
    else:
        y_okay = flin(y2, px, y1)

    return x_okay and y_okay

def rectangle_inside(tlx1, tly1, brx1, bry1, tlx2, tly2, brx2, bry2):
    x_in = flin(tlx2, tlx1, brx2) and flin(tlx2, brx1, brx2)
    y_in = flin(tly2, tly1, bry2) and flin(tly2, bry1, bry2)

    return x_in and y_in

def rectangle_overlay(tlx1, tly1, brx1, bry1, tlx2, tly2, brx2, bry2):
    x_off = brx1 < tlx2 or tlx1 > brx2
    y_off = bry1 < tly2 or tly1 > bry2

    return not (x_off or y_off)

def rectangle_contain(tlx, tly, brx, bry, x, y):
    return flin(tlx, x, brx) and flin(tly, y, bry)

###################################################################################################
def lines_intersection(x11, y11, x12, y12, x21, y21, x22, y22):
    '''
     find the intersection point P(px, py) of L1((x11, y11), (x12, y12)) and L2((x21, y21), (x22, y22))
    '''

    denominator = ((x11 - x12) * (y21 - y22) - (y11 - y12) * (x21 - x22))
    intersected = (denominator != 0.0)
    
    if intersected:
        T1 = +((x11 - x21) * (y21 - y22) - (y11 - y21) * (x21 - x22)) / denominator
        T2 = -((x11 - x12) * (y11 - y21) - (y11 - y12) * (x11 - x21)) / denominator
        px = x21 + T2 * (x22 - x21)
        py = y21 + T2 * (y22 - y21)
    else:
        px = py = T1 = T2 = math.nan

    return px, py, T1, T2
