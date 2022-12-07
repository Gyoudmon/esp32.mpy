import sdl2

from .forward import *
from .graphics.image import *
from .virtualization.iscreen import *


###############################################################################
class IMatterInfo(object):
    def __init__(self, master):
        self.master = master

class IMatter(object):
    def __init__(self):
        super(IMatter, self).__init__()
        self.info = None
        self.__resize_anchor, self.__resizable = MatterAnchor.LT, False
        self.__anchor, self.__anchor_x, self.__anchor_y = MatterAnchor.LT, 0.0, 0.0
        self.__deal_with_events, self.__deal_with_low_level_events = False, False
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
    def draw(self, renderer, X, Y, Width, Height): pass
    def ready(self): return True

# public
    def own_caret(self, x, y): pass

    def has_caret(self):
        careted = False

        if self.info:
            careted = (self.info.master.get_focused_matter == self)

        return careted

# public
    def is_colliding_with_mouse(self, local_x, local_y): return True
    def on_char(self, key, modifiers, repeats, pressed): return False
    def on_text(self, text, size, entire): return False
    def on_editing_text(self, text, pos, span): return False
    def on_hover(self, local_x, local_y): return False
    def on_tap(self, local_x, local_y): return False
    def on_goodbye(self, local_x, local_y): return False

    def start_input_text(self, prompt): pass
    def log_message(self, message): pass

# public
    def on_pointer_pressed(self, button, x, y, clicks, touch): return False
    def on_pointer_released(self, button, x, y, clicks, touch): return False
    def on_pointer_move(self, state, x, y, dx, dy, touch): return False
    
# public
    def enable_events(self, yes_or_no, low_level = False):
        self.__deal_with_events = yes_or_no
        self.__deal_with_low_level_events = low_level
    
    def enable_resizing(self, yes_no, anchor = MatterAnchor.CC):
        self.__resizable = yes_no
        self.__resize_anchor = anchor

    def resizable(self):
        return self.__resizable, self.__resize_anchor

    def events_allowed(self):
        return self.__deal_with_events

    def low_level_events_allowed(self):
        return self.events_allowed() and self.__deal_with_low_level_events

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

    def log_message(self, message):
        if self.info:
            self.info.master.log_message(message)
    
    def camouflage(self, yes_or_no):
        self.__findable = yes_or_no
    
    def concealled(self):
        return not self.__findable

# public
    def snapshot(self):
        width, height = self.get_extent(0.0, 0.0)
        photograph = game_blank_image(width, height)

        if photograph:
            renderer = sdl2.SDL_CreateSoftwareRenderer(photograph)

            if renderer:
                self.draw(renderer, 0.0, 0.0, width, height)
                sdl2.SDL_RenderPresent(renderer)
                sdl2.SDL_DestroyRenderer(renderer)

        return photograph                

    def save_snapshot(self, pname):
        photograph = self.snapshot()
        okay = game_save_image(photograph, pname)

        sdl2.SDL_FreeSurface(photograph)

        return okay

# proteceted
    def _on_resized(self, width, height, old_width, old_height):
        pass
