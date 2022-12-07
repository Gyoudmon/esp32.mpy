import sdl2                 # 原始 SDL2 函数
import sdl2.pixels as sdlp  # 原始 SDL2 像素结构体
import ctypes as ffi        # 外语接口

import sys
import enum

from .font import *
from .colorspace import *
from .geometry import *

###################################################################################################
class TextRenderMode(enum.Enum):
    Solid = 0x44215fc76574b744
    Shaded = 0x457cf9960addbe59
    LCD = 0x4873c4e96fb8ba72
    Blender = 0x470c7b0ea6e5d96f

###################################################################################################
def game_text_size(font, width, height, text):
    if not font: 
        font = game_font.DEFAULT

    return _unsafe_utf8_size(font, text)

###################################################################################################
def game_text_surface(rtext, font, mode, fgc, bgc, wrap = 0):
    text = rtext.encode('utf-8')

    if not font:
        font = game_font.DEFAULT
    
    if sys.platform == 'win32':
        if mode == TextRenderMode.Solid:
            surface = sdl2.sdlttf.TTF_RenderUTF8_Solid(font, text, fgc)
        elif mode == TextRenderMode.Blender:
            surface = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, text, fgc)
        else:
            surface = sdl2.sdlttf.TTF_RenderUTF8_Shaded(font, text, fgc, bgc)
    else:
        if wrap >= 0: # will wrap by newline for 0
            if mode == TextRenderMode.Solid:
                surface = sdl2.sdlttf.TTF_RenderUTF8_Solid_Wrapped(font, text, fgc, wrap)
            elif mode == TextRenderMode.Blender:
                surface = sdl2.sdlttf.TTF_RenderUTF8_Blended_Wrapped(font, text, fgc, wrap)
            elif mode == TextRenderMode.LCD:
                surface = sdl2.sdlttf.TTF_RenderUTF8_LCD_Wrapped(font, text, fgc, bgc, wrap)
            else:
                surface = sdl2.sdlttf.TTF_RenderUTF8_Shaded_Wrapped(font, text, fgc, bgc, wrap)
        else:
            if mode == TextRenderMode.Solid:
                surface = sdl2.sdlttf.TTF_RenderUTF8_Solid(font, text, fgc)
            elif mode == TextRenderMode.Blender:
                surface = sdl2.sdlttf.TTF_RenderUTF8_Blended(font, text, fgc)
            elif mode == TextRenderMode.LCD:
                surface = sdl2.sdlttf.TTF_RenderUTF8_LCD(font, text, fgc, bgc)
            else:
                surface = sdl2.sdlttf.TTF_RenderUTF8_Shaded(font, text, fgc, bgc)

    if not surface:
        print("无法渲染文本: " + sdl2.sdlttf.TTF_GetError().decode('utf-8'))

    return surface

###################################################################################################
def game_draw_solid_text(font, renderer, rgb, x, y, text, wrap = 0):
    message = _solid_text_surface(font, rgb, text, wrap)
    _safe_render_text_surface(renderer, message, x, y)

def game_draw_shaded_text(font, renderer, fgc, bgc, x, y, text, wrap = 0):
    message = _shaded_text_surface(font, fgc, bgc, text, wrap)
    _safe_render_text_surface(renderer, message, x, y)

def game_draw_lcd_text(font, renderer, fgc, bgc, x, y, text, wrap = 0):
    message = _lcd_text_surface(font, fgc, bgc, text, wrap)
    _safe_render_text_surface(renderer, message, x, y)

def game_draw_blended_text(font, renderer, rgb, x, y, text, wrap = 0):
    message = _blended_text_surface(font, rgb, text, wrap)
    _safe_render_text_surface(renderer, message, x, y)

###################################################################################################
def _unsafe_utf8_size(font, text):
    w = ffi.c_int(0)
    h = ffi.c_int(0)

    if sdl2.sdlttf.TTF_SizeUTF8(font, text.encode('utf-8'), ffi.byref(w), ffi.byref(h)) == -1:
        print("无法计算文本尺寸: " + sdl2.sdlttf.TTF_GetError().decode('utf-8'))

    return (w.value, h.value)

def _hex_rgb_to_color(rgb):
    r, g, b = RGB_FromHexadecimal(rgb)

    return sdlp.SDL_Color(r, g, b, 255)

def _safe_render_text_surface(target, message, x, y):
    if message:
        game_render_surface(target, message, [x, y])
        sdl2.SDL_FreeSurface(message)

def _solid_text_surface(font, rgb, text, wrap):
    text_color = _hex_rgb_to_color(rgb)

    return game_text_surface(text, font, TextRenderMode.Solid, text_color, text_color, wrap)

def _shaded_text_surface(font, fgc, bgc, text, wrap):
    text_color = _hex_rgb_to_color(fgc)
    background_color = _hex_rgb_to_color(bgc)

    return game_text_surface(text, font, TextRenderMode.Shaded, text_color, background_color, wrap)

def _lcd_text_surface(font, fgc, bgc, text, wrap):
    text_color = _hex_rgb_to_color(fgc)
    background_color = _hex_rgb_to_color(bgc)

    return game_text_surface(text, font, TextRenderMode.LCD, text_color, background_color, wrap)

def _blended_text_surface(font, rgb, text, wrap):
    text_color = _hex_rgb_to_color(rgb)

    return game_text_surface(text, font, TextRenderMode.Blender, text_color, text_color, wrap)
