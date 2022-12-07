import sys              # 系统相关参数和函数
import os               # 操作系统相关函数
import ctypes           # 外语接口
import atexit           # 用于管理程序退出时执行的函数
import datetime         # 日期时间相关函数

import sdl2             # 原始 (C 风格) SDL2 函数
import sdl2.rect        # 原始 (C 风格) SDL2 Rect 结构体
import sdl2.sdlttf      # 原始 (C 风格) SDL2_TTF 函数
import sdl2.sdlimage    # 原始 (C 风格) SDL2_Image 函数

import sdl2.ext         # Python 风格的 SDL2 函数

from .graphics.font import *
from .graphics.text import *
from .graphics.colorspace import *

from .virtualization.display import *

###############################################################################
def game_initialize(flags, fontsize = 16):
    if game_font.DEFAULT is None:
        _Call_With_Safe_Exit(sdl2.SDL_Init(flags), "SDL 初始化失败：", sdl2.SDL_Quit)
        _Call_With_Safe_Exit(sdl2.sdlttf.TTF_Init(), "TTF 初始化失败：", sdl2.sdlttf.TTF_Quit, sdl2.sdlttf.TTF_GetError)

        if sys.platform == "darwin":
            sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_JPG | sdl2.sdlimage.IMG_INIT_PNG)
        else:
            sdl2.sdlimage.IMG_Init(sdl2.sdlimage.IMG_INIT_PNG)
    
        maybe_err = sdl2.sdlimage.IMG_GetError()
        if len(maybe_err):
            print("IMG 初始化失败：" + maybe_err)
            os._exit(1)

        game_fonts_initialize(fontsize)

        atexit.register(sdl2.sdlimage.IMG_Quit)
        # atexit.register(game_fonts_destroy) # leave it to ctypes

def game_create_texture(window, renderer):
    width, height = _get_window_size(window, renderer)
    t = sdl2.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_TARGET, width, height)
    _Check_Variable_Validity(t, None, "SDL 纹理创建失败：")

    return t

def game_world_create(width, height):
    cpos = sdl2.SDL_WINDOWPOS_CENTERED
    flags = sdl2.SDL_WINDOW_SHOWN | sdl2.SDL_WINDOW_RESIZABLE

    if width <= 0 or height <= 0:
        if width <= 0 and height <= 0:
            flags |= sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP
        else:
            flags |= sdl2.SDL_WINDOW_MAXIMIZED

    w = sdl2.SDL_CreateWindow("The Big Bang".encode("utf-8"), cpos, cpos, width, height, flags)
    _Check_Variable_Validity(w, None, "SDL 窗体创建失败：")

    r = sdl2.SDL_CreateRenderer(w, -1, sdl2.SDL_RENDERER_ACCELERATED)
    _Check_Variable_Validity(r, None, "SDL 渲染器创建失败：")

    return w, r

def game_world_reset(renderer, fgc, bgc, texture = None):
    fcr, fcg, fcb = RGB_FromHexadecimal(fgc)
    bcr, bcg, bcb = RGB_FromHexadecimal(bgc)

    if texture:
        sdl2.SDL_SetRenderTarget(renderer, texture)

    sdl2.SDL_SetRenderDrawColor(renderer, bcr, bcg, bcb, 255)
    sdl2.SDL_RenderClear(renderer)
    sdl2.SDL_SetRenderDrawColor(renderer, fcr, fcg, fcb, 255)

def game_world_refresh(renderer, texture):
    sdl2.SDL_SetRenderTarget(renderer, None)
    sdl2.SDL_RenderCopy(renderer, texture, None, None)
    sdl2.SDL_RenderPresent(renderer)
    sdl2.SDL_SetRenderTarget(renderer, texture)

###############################################################################
class Universe(IDisplay):
# public
    def __init__(self, fps = 60, fgc = 0x0000000, bgc = 0xFFFFFF):
        """ 构造函数，在创建游戏世界时自动调用，以设置帧频、窗口标题、前背景色和混色模式 """
        
        # The constructors of base classes must be invoked explicitly
        # even if there is only one that has no argument
        super(Universe, self).__init__()
        
        game_initialize(sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_TIMER)
        
        # Please search "Python sequence unpacking"(序列解包)
        self.__window, self.__renderer = game_world_create(1, 0)
        self.__texture = None
        self.__window_width, self.__window_height = 0, 0
        self.__fgc, self.__bgc = fgc, bgc
        self.__timer, self.__fps = 0, fps

        game_world_reset(self.__renderer, self.__fgc, self.__bgc, self.__texture)

        self.set_blend_mode(sdl2.SDL_BLENDMODE_NONE)
        self.__echo, self.__echo_font = sdl2.rect.SDL_Rect(0, 0, 0, 0), None
        self.__ifgc, self.__ibgc, self.__mfgc = fgc, bgc, fgc

        self.__current_usrin, self.__prompt, self.__usrin, self.__message = "", "", "", ""
        self.__in_editing, self.__needs_termio_if_no_echo = False, False
        self.__snapshot_rootdir = ""
        
        # Python doesn't need two-step initialization as C++ does
        self.construct(sys.argv)

    def __del__(self):
        """ 析构函数，在对象被销毁时自动调用，默认销毁游戏宇宙 """

        if self.__timer > 0:
            sdl2.SDL_RemoveTimer(self.__timer)

        if self.__texture:
            sdl2.SDL_DestroyTexture(self.__texture)

        if self.__renderer:
            sdl2.SDL_DestroyRenderer(self.__renderer)

        if self.__window:
            sdl2.SDL_DestroyWindow(self.__window)

# public
    def construct(self, argv):
        """ 给游戏世界一个解析命令行参数的机会，默认什么都不做 """
        pass

    def reflow(self, width, height):
        """ 排列可视化元素，在合适的时候自动调用，默认什么都不做 """
        pass

    def update(self, interval, count, uptime):
        """ 更新游戏世界，定时器到期时自动调用，默认什么都不做 """
        pass

    def draw(self, renderer, x, y, width, height):
        """ 绘制游戏世界，在合适的时候自动调用，默认什么都不做 """
        pass

    def can_exit(self):
        """ 告诉游戏主循环，是否游戏已经结束可以退出了，默认永久运行 """
        return False

    def big_bang(self):
        """ 宇宙大爆炸，开启游戏主循环，返回游戏运行时间 """
        quit_time = 0

        if self.__fps > 0:
            parcel = _TimerParcel(ffi.py_object(self), 1000 // self.__fps, 0, 0)
            p_parcel = ffi.cast(ffi.pointer(parcel), ffi.c_void_p)
            self.__timer = sdl2.SDL_AddTimer(parcel.interval, sdl2.SDL_TimerCallback(_trigger_timer_event), p_parcel)
            _Check_Variable_Validity(self.__timer, 0, "定时器创建失败: ")

        self.__window_width, self.__window_height = self.get_window_size()
        self.begin_update_sequence()
        self._on_big_bang(self.__window_width, self.__window_height)
        self._on_resize(self.__window_width, self.__window_height)
        self.notify_updated()
        self.end_update_sequence()
        
        while (quit_time == 0) and not self.can_exit():
            for e in sdl2.ext.get_events():
                self.begin_update_sequence()

                match e.type:
                    case sdl2.SDL_USEREVENT:
                        parcel = ffi.cast(e.user.data1, ffi.POINTER(_TimerParcel)).contents
                        if parcel.master is self:
                            self._on_elapse(parcel.interval, parcel.count, parcel.uptime)
                    case sdl2.SDL_MOUSEMOTION: self._on_mouse_motion_event(e.motion)
                    case sdl2.SDL_MOUSEWHEEL: self._on_mouse_wheel_event(e.wheel)
                    case sdl2.SDL_MOUSEBUTTONUP: self._on_mouse_button_event(e.button, False)
                    case sdl2.SDL_MOUSEBUTTONDOWN: self._on_mouse_button_event(e.button, True)
                    case sdl2.SDL_KEYUP: self._on_keyboard_event(e.key, False)
                    case sdl2.SDL_KEYDOWN: self._on_keyboard_event(e.key, True)
                    case sdl2.SDL_TEXTINPUT: self._on_user_input(e.text.text.decode('utf-8'))
                    case sdl2.SDL_TEXTEDITING: self._on_editing(e.edit.text.decode('utf-8'), e.edit.start, e.edit.length)
                    case sdl2.SDL_WINDOWEVENT:
                        match e.window.event:
                             case sdl2.SDL_WINDOWEVENT_RESIZED: self._on_resize(e.window.data1, e.window.data2)    
                    case sdl2.SDL_QUIT:
                        if self.__timer > 0:
                            sdl2.SDL_RemoveTimer(self.__timer)
                            self.__timer = 0

                        quit_time = e.quit.timestamp
        
                self.end_update_sequence()

# public
    def set_snapshot_folder(self, path):
        self.__snapshot_rootdir = os.path.normpath(path)

    def snapshot(self):
        photograph = game_blank_image(self.__window_width, self.__window_height)

        if photograph:
            renderer = sdl2.SDL_CreateSoftwareRenderer(photograph)

            if renderer:
                self.__do_redraw(renderer, 0, 0, self.__window_width, self.__window_height)
                sdl2.SDL_RenderPresent(renderer)
                sdl2.SDL_DestroyRenderer(renderer)

        return photograph

# public
    def set_blend_mode(self, bmode):
        sdl2.SDL_SetRenderDrawBlendMode(self.__renderer, bmode)

    def set_window_title(self, title):
        sdl2.SDL_SetWindowTitle(self.__window, title.encode("utf-8"))

    def set_window_size(self, width, height, centerize = True):
        sdl2.SDL_SetWindowSize(self.__window, width, height)

        if centerize:
            sdl2.SDL_SetWindowPosition(self.__window, sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED)
        
        if self.__texture:
            self._on_resize(width, height)  # the universe has been completely initialized
        else:
            pass                            # the big_bang() will do resizing later

    def set_window_fullscreen(self, yes):
        if yes:
            sdl2.SDL_SetWindowFullscreen(self.__window, sdl2.SDL_WINDOW_FULLSCREEN_DESKTOP)
        else:
            sdl2.SDL_SetWindowFullscreen(self.__window, 0)

    def get_window_size(self, logical = True):
        return _get_window_size(self.__window, self.__renderer, logical)

    def get_renderer_name(self):
        rinfo = sdl2.render.SDL_RendererInfo()

        sdl2.SDL_GetRendererInfo(self.__renderer, ctypes.byref(rinfo))

        return rinfo.name.decode('utf-8')

    def get_foreground_color(self):
        return self.__fgc

    def get_background_color(self):
        return self.__bgc

    def get_frame_per_second(self):
        return self.__fps

# public
    def get_extent(self):
        return self.get_window_size()

    def refresh(self):
        self.__do_redraw(self.__renderer, 0, 0, self.__window_width, self.__window_height)
        game_world_refresh(self.__renderer, self.__texture)

    def set_cmdwin_height(self, cmdwinheight, fgc = -1, bgc = -1, font = game_font.unicode):
        _, height = _get_window_size(self.__window, self.__renderer)
        self.__echo.y = height - cmdwinheight
        self.__echo.h = cmdwinheight

        if fgc < 0:
            self.__ifgc = self.__fgc
        else:
            self.__ifgc = fgc

        if bgc < 0:
            self.__ibgc = self.__bgc
        else:
            self.__ibgc = bgc

        self.__echo_font = font
        sdl2.SDL_SetTextInputRect(self.__echo)
    
    def get_cmdwin_height(self):
        return self.__echo.h

# public
    def log_message(self, args):
        if isinstance(args, str):
            self.__message = args
        else:
            self.__message = args[1]
            if args[0] >= 0:
                self.__mfgc = args[0]
        
        self.__needs_termio_if_no_echo = True

        if self.__display_usr_message(self.__renderer):
            self.notify_updated()

    def start_input_text(self, prompt):
        if prompt:
            self.__prompt = prompt

        sdl2.SDL_StartTextInput()
        self.__in_editing = True
        self.__message = ""

        if self.__display_usr_input_and_caret(self.__renderer, True):
            self.notify_updated()

    def stop_input_text(self):
        self.__in_editing = False
        sdl2.SDL_StopTextInput()
        self._on_text(self.__usrin, len(self.__usrin), True)
        self.__usrin = ""
        self.__prompt = ""

        if self.__display_usr_input_and_caret(self.__renderer, True):
            self.notify_updated()

# protected (virtual, default)
    def _on_click(self, x, y): pass                                         # 处理单击事件
    def _on_right_click(self, x, y): pass                                   # 处理右击事件
    def _on_double_click(self, x, y): pass                                  # 处理双击事件
    def _on_mouse_move(self, state, x, y, dx, dy): pass                     # 处理移动事件
    def _on_scroll(self, horizon, vertical, hprecise, vprecise): pass       # 处理滚轮事件

    def _on_char(self, key, modifiers, repeats, pressed): pass              # 处理键盘事件
    def _on_text(self, text, size, entire): pass                            # 处理文本输入事件
    def _on_editing_text(self, text, pos, span): pass                       # 处理文本输入事件
            
    def _on_save(self): pass                                                # 处理保存事件

# protected
    def _draw_cmdwin(self, renderer, x, y, width, height):
        game_draw_line(renderer, x, y, width, y, 0x888888)

# protected
    # 大爆炸之前最后的初始化宇宙机会，默认什么都不做
    def _on_big_bang(self, width, height): pass

    # 响应定时器事件，刷新游戏世界
    def _on_elapse(self, interval, count, uptime):
        """ 响应定时器事件，刷新游戏世界 """
        self.update(interval, count, uptime)
        self.notify_updated()

    # 响应鼠标事件，并按需触发单击、右击、双击、移动、滚轮事件
    def _on_mouse_button_event(self, mouse, pressed):
        if not pressed:
            match mouse.clicks:
                case 1:
                    match mouse.button:
                        case sdl2.SDL_BUTTON_LEFT: self._on_click(mouse.x, mouse.y)
                        case sdl2.SDL_BUTTON_RIGHT: self._on_right_click(mouse.x, mouse.y)
                case 2:
                    match mouse.button:
                        case sdl2.SDL_BUTTON_LEFT: self._on_double_click(mouse.x, mouse.y)

    def _on_mouse_motion_event(self, mouse):
        self._on_mouse_move(mouse.state, mouse.x, mouse.y, mouse.xrel, mouse.yrel)

    def _on_mouse_wheel_event(self, mouse):
        horizon = mouse.x
        vertical = mouse.y
        hprecise = float(horizon)  # mouse.preciseX
        vprecise = float(vertical) # mouse.preciseY

        if mouse.direction == sdl2.SDL_MOUSEWHEEL_FLIPPED:
            horizon  *= -1
            vertical *= -1
            hprecise *= -1.0
            vprecise *= -1.0

        self._on_scroll(horizon, vertical, hprecise, vprecise)

    # 响应键盘事件，并按需触发按下、松开事件
    def _on_keyboard_event(self, keyboard, pressed):
        key = keyboard.keysym
        keycode = key.sym

        if keycode <= 0x110000:
            keycode = chr(keycode)

        if self.__in_editing:
            if not pressed:
                match key.sym:
                    case sdl2.SDLK_RETURN: self.__enter_input_text()
                    case sdl2.SDLK_BACKSPACE: self.__popback_input_text()
        else:
            if not pressed:
                ctrl_mod = sdl2.KMOD_LCTRL | sdl2.KMOD_RCTRL

                if sys.platform == 'darwin':
                    ctrl_mod = ctrl_mod | sdl2.KMOD_LGUI | sdl2.KMOD_RGUI

                if key.mod & ctrl_mod:
                    match key.sym:
                        case sdl2.SDLK_s: self._on_save()
                        case sdl2.SDLK_p: self._take_snapshot()
                        case _: self._on_char(keycode, key.mod, keyboard.repeat, pressed)
                else:
                    self._on_char(keycode, key.mod, keyboard.repeat, pressed)
            else:
                self._on_char(keycode, key.mod, keyboard.repeat, pressed)

    # 响应窗体事件，并按需触发尺寸改变事件
    def _on_resize(self, width, height):
        self.__window_width, self.__window_height = width, height

        if self.__echo.h > 0:
            self.__echo.y = height - self.__echo.h
            self.__echo.w = width

        if self.__texture:
            sdl2.SDL_DestroyTexture(self.__texture)

        self.__texture = game_create_texture(self.__window, self.__renderer)

        self.begin_update_sequence()
        game_world_reset(self.__renderer, self.__fgc, self.__bgc, self.__texture)
        self.reflow(width, height - self.get_cmdwin_height())
        self.notify_updated()
        self.end_update_sequence()

    # 响应输入法事件，按需显示用户输入的内容
    def _on_user_input(self, text):
        if self.__in_editing:
            self.__usrin += text
            self.__current_usrin = ""

            if self.__display_usr_input_and_caret(self.__renderer, True):
                self.notify_updated()

        self._on_text(text, len(text), False)

    def _on_editing(self, text, pos, span):
        self.__current_usrin = text
        self._on_editing_text(text, pos, span)

    # 处理预设事件
    def _take_snapshot(self):
        bname = sdl2.SDL_GetWindowTitle(self.__window).decode('utf-8')
        dtime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        basename = "%s-%s.png" % (bname, dtime)

        if self.__snapshot_rootdir:
            snapshot_png = self.__snapshot_rootdir + os.sep + basename
        else:
            snapshot_png = os.getcwd() + os.sep + basename

        if self.save_snapshot(snapshot_png):
            self.log_message((self.__fgc, "A snapshot has been save as '%s'." % snapshot_png))
        else:
            self.log_message((0xFF0000, "Failed to save snapshot: %s." % sdl2.SDL_GetError().decode("utf-8")))

# private
    def __do_redraw(self, renderer, x, y, width, height):
        game_world_reset(renderer, self.__fgc, self.__bgc)
        self.draw(renderer, x, y, width, height - self.get_cmdwin_height())

        if self.__in_editing:
            self.__display_usr_input_and_caret(renderer, True)
        else:
            self.__display_usr_message(renderer)

        if self.__echo.h > 0:
            self._draw_cmdwin(renderer, self.__echo.x, self.__echo.y, self.__echo.w, self.__echo.h)

    def __display_usr_input_and_caret(self, renderer, yes):
        updated = (self.__echo.h > 0)

        if updated:
            game_fill_rect(renderer, self.__echo.x, self.__echo.y, self.__echo.w, self.__echo.h, self.__ibgc, 0xFF)

            if yes:
                if self.__prompt:
                    game_draw_blended_text(self.__echo_font, renderer, self.__ifgc,
                        self.__echo.x, self.__echo.y, self.__prompt + self.__usrin + "_", self.__echo.w)
                else:
                    game_draw_blended_text(self.__echo_font, renderer, self.__ifgc,
                        self.__echo.x, self.__echo.y, self.__usrin + "_", self.__echo.w)

        return updated

    def __display_usr_message(self, renderer):
        updated = (self.__echo.h > 0)
        
        if updated:
            game_fill_rect(renderer, self.__echo.x, self.__echo.y, self.__echo.w, self.__echo.h, self.__ibgc, 0xFF)

            if self.__message:
                game_draw_blended_text(self.__echo_font, renderer, self.__mfgc,
                    self.__echo.x, self.__echo.y, self.__message, self.__echo.w)
        else:
            if self.__message:
                if self.__needs_termio_if_no_echo:
                    print(self.__message)
                    self.__needs_termio_if_no_echo = False

        return updated

    def __enter_input_text(self):
        if self.__current_usrin:
            self._on_user_input(self.__current_usrin)
            self.__current_usrin = ""
        else:
            self.stop_input_text()

    def __popback_input_text(self):
        if self.__usrin:
            self.__usrin = self.__usrin[0:-1]

            if self.__display_usr_input_and_caret(self.__renderer, True):
                self.notify_updated()

###############################################################################
def _Call_With_Error_Message(init, message, GetError):
    if init != 0:
        print(message + GetError().decode("utf-8"))
        os._exit(1)
    
def _Call_With_Safe_Exit(init, message, fquit, GetError = sdl2.SDL_GetError):
    _Call_With_Error_Message(init, message, GetError)
    atexit.register(fquit)

def _Check_Variable_Validity(init, failure, message, GetError = sdl2.SDL_GetError):
    if init == failure:
        print(message + GetError().decode("utf-8"))
        os._exit(1)

def _get_window_size(window, renderer, logical = True):
    w = ctypes.c_int()
    h = ctypes.c_int()
    
    if logical:
        sdl2.SDL_GetRendererOutputSize(renderer, ctypes.byref(w), ctypes.byref(h))
    else:
        sdl2.SDL_GetWindowSize(window, ctypes.byref(w), ctypes.byref(h))

    return w.value, h.value

###############################################################################
class _TimerParcel(ffi.Structure):
    _fields_ = [("master", ffi.py_object),
                ("interval", ffi.c_int),
                ("count", ffi.c_int),
                ("uptime", ffi.c_int)]

def _trigger_timer_event(interval, datum):
    """ 本函数在定时器到期时执行, 并将该事件报告给事件系统，以便绘制下一帧动画
    
    :param interval: 定时器等待时长，以 ms 为单位
    :param datum:    用户数据，传递给 SDL_AddTimer 的第三个参数会出现在这
    
    :returns: 返回定时器下次等待时间。注意定时器的实际等待时间是该返回值减去执行该函数所花时间
    """

    parcel = ffi.cast(datum, ffi.POINTER(_TimerParcel)).contents
    parcel.count += 1
    parcel.interval = interval
    parcel.uptime = sdl2.SDL_GetTicks()    

    user_event = sdl2.SDL_UserEvent()
    timer_event = sdl2.SDL_Event()

    user_event.type = sdl2.SDL_USEREVENT
    user_event.code = 0
    user_event.data1 = ffi.cast(ffi.pointer(parcel), ffi.c_void_p)

    # 将该事件报告给事件系统
    timer_event.type = user_event.type
    timer_event.user = user_event
    sdl2.SDL_PushEvent(ffi.byref(timer_event))

    return interval
