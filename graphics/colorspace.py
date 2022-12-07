import sdl2  # SDL2 函数
import math  # 数学函数

###############################################################################
def RGB_SetRenderDrawColor(renderer, rgb, alpha = 0xFF):
    r, g, b = RGB_FromHexadecimal(rgb)
    
    if isinstance(alpha, float):
        alpha = _UCHAR(alpha)
    
    return sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, alpha)

def HSV_SetRenderDrawColor(renderer, hue, saturation, value, alpha = 0xFF):
    chroma = saturation * value
    m = value - chroma

    return _set_renderer_color_from_hue(renderer, hue, chroma, m, alpha)

def HSL_SetRenderDrawColor(renderer, hue, saturation, lightness, alpha = 0xFF):
    chroma = saturation * (1.0 - math.fabs(lightness * 2.0 - 1.0))
    m = lightness - chroma * 0.5
    
    return _set_renderer_color_from_hue(renderer, hue, chroma, m, alpha)

def HSI_SetRenderDrawColor(renderer, hue, saturation, intensity, alpha = 0xFF):
    if (saturation == 0.0) or math.isnan(saturation):
        return _set_renderer_draw_color(renderer, intensity, intensity, intensity, alpha)
    elif (hue < 120.0):
        return _set_renderer_color_from_hsi_sector(renderer, hue, saturation, intensity, _R, alpha)
    elif (hue < 240.0):
        return _set_renderer_color_from_hsi_sector(renderer, hue - 120.0, saturation, intensity, _G, alpha)
    else:
        return _set_renderer_color_from_hsi_sector(renderer, hue - 240.0, saturation, intensity, _B, alpha)

###############################################################################
def RGB_FromHexadecimal(hex):
    return (hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF

def RGBA_FromHexadecimal(hex):
    return (hex >> 24) & 0xFF, (hex >> 16) & 0xFF, (hex >> 8) & 0xFF, hex & 0xFF

def RGB_FillColor(c, hex, alpha = 0xFF):
    c.r, c.g, c.b = RGB_FromHexadecimal(hex)
    a = alpha

    if isinstance(a, float):
        a = _UCHAR(a)

    c.a = a

###############################################################################
_R = 1
_G = 2
_B = 3

def _UCHAR(v):
    return round(v * 255.0)

def _set_renderer_draw_color(renderer, r, g, b, a):
    if isinstance(a, float):
        a = _UCHAR(a)
    
    return sdl2.SDL_SetRenderDrawColor(renderer, _UCHAR(r), _UCHAR(g), _UCHAR(b), a)

def _set_renderer_color_from_hue(renderer, hue, chroma, m, a):
    r = m
    g = m
    b = m
    
    if math.isnan(hue):
        hue_60 = hue / 60.0
        flhue = math.floor(hue_60)
        fxhue = int(flhue)
        x = chroma * (1.0 - math.fabs(float(fxhue % 2) - (flhue - hue_60) - 1.0))
        
        if fxhue == 0:
            r += chroma
            g += x
        elif fxhue == 1:
            r += x
            g += chroma
        elif fxhue == 2:
            g += chroma
            b += x
        elif fxhue == 3:
            g += x
            b += chroma
        elif fxhue == 4:
            r += x
            b += chroma
        elif fxhue == 5:
            r += chroma
            b += x

    return _set_renderer_draw_color(renderer, r, g, b, a)

def _set_renderer_color_from_hsi_sector(renderer, hue, saturation, intensity, color_component, alpha):
    cosH_60H = 2.0  # if hue == 0.0 or hue == 120.0

    if (hue != 0.0) and (hue != 120.0):
        H = hue * (math.pi / 180.0)
        cosH_60H = math.cos(H) / math.cos(math.pi / 3.0 - H)

    major = intensity * (1.0 + saturation * cosH_60H)
    midor = intensity * (1.0 - saturation)
    minor = (intensity * 3.0) - (major + midor)

    if color_component == _R:
        return _set_renderer_draw_color(renderer, major, minor, midor, alpha)
    elif color_component == _G:
        return _set_renderer_draw_color(renderer, midor, major, minor, alpha)
    else:
        return _set_renderer_draw_color(renderer, minor, midor, major, alpha)
