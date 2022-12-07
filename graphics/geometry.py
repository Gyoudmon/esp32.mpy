import sdl2                             # 原始 SDL2 函数
import sdl2.rect as sdlr                # 原始 SDL2 矩形结构体
import ctypes as ffi                    # 外语接口函数
import math                             # 基础数学函数

from .colorspace import *               # 色彩空间相关函数, 前面那个点指代相对本文件的路径
from ..physics.mathematics import *     # 图形学、线性代数相关函数

###############################################################################
def game_draw_point(renderer, x, y, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    sdl2.SDL_RenderDrawPoint(renderer, round(x), round(y))

def game_draw_line(renderer, x1, y1, x2, y2, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    sdl2.SDL_RenderDrawLine(renderer, round(x1), round(y1), round(x2), round(y2))

def game_draw_rect(renderer, x, y, width, height, cs, alpha = 0xFF):
    box = sdlr.SDL_Rect(round(x), round(y), round(width), round(height))

    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    sdl2.SDL_RenderDrawRect(renderer, ffi.byref(box))

def game_fill_rect(renderer, x, y, width, height, cs, alpha = 0xFF):
    box = sdlr.SDL_Rect(round(x), round(y), round(width), round(height))

    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    sdl2.SDL_RenderFillRect(renderer, ffi.byref(box))

def game_draw_square(renderer, cx, cy, apothem, cs, alpha = 0xFF):
    game_draw_rect(renderer, cx - apothem, cy - apothem, apothem * 2, apothem * 2, cs, alpha)

def game_fill_square(renderer, cx, cy, apothem, cs, alpha = 0xFF):
    game_fill_rect(renderer, cx - apothem, cy - apothem, apothem * 2, apothem * 2, cs, alpha)

def game_draw_circle(renderer, cx, cy, radius, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    _draw_circle(renderer, cx, cy, radius)

def game_fill_circle(renderer, cx, cy, radius, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    _fill_circle(renderer, cx, cy, radius)

def game_draw_ellipse(renderer, cx, cy, aradius, bradius, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    _draw_ellipse(renderer, cx, cy, aradius, bradius)

def game_fill_ellipse(renderer, cx, cy, aradius, bradius, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)

    _fill_ellipse(renderer, cx, cy, aradius, bradius)

def game_draw_regular_polygon(renderer, n, cx, cy, radius, rotation, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)    
        
    _draw_regular_polygon(renderer, n, cx, cy, radius, rotation)

def game_fill_regular_polygon(renderer, n, cx, cy, radius, rotation, cs, alpha = 0xFF):
    if isinstance(cs, int):
        RGB_SetRenderDrawColor(renderer, cs, alpha)
    else:
        HSV_SetRenderDrawColor(renderer, cs[0], cs[1], cs[2], alpha)    
        
    _fill_regular_polygon(renderer, n, cx, cy, radius, rotation)

###############################################################################
def game_render_surface(target, psurface, region):
    texture = sdl2.SDL_CreateTextureFromSurface(target, psurface)

    if not isinstance(region, sdlr.SDL_Rect):
        surface = psurface.contents # `contents` creates new instance every time
        region = sdlr.SDL_Rect(round(region[0]), round(region[1]), surface.w, surface.h)

    if texture:
        sdl2.SDL_RenderCopy(target, texture, None, region)
        sdl2.SDL_DestroyTexture(texture)

###############################################################################
def _draw_circle(renderer, cx, cy, radius):
    cx, cy, radius = round(cx), round(cy), round(radius)
    err = 2 - 2 * radius
    x = -radius
    y = 0
    
    while True:
        sdl2.SDL_RenderDrawPoint(renderer, cx + x, cy - y)
        sdl2.SDL_RenderDrawPoint(renderer, cx - x, cy + y)
        sdl2.SDL_RenderDrawPoint(renderer, cx + y, cy + x)
        sdl2.SDL_RenderDrawPoint(renderer, cx - y, cy - x)

        radius = err
        if radius <= y:
            y += 1
            err += y * 2 + 1

        if (radius > x) or (err > y):
            x += 1
            err += x * 2

        if x >= 0: break

def _fill_circle(renderer, cx, cy, radius):
    cx, cy, radius = round(cx), round(cy), round(radius)
    err = 2 - 2 * radius
    x = -radius
    y = 0
    
    while True:
        sdl2.SDL_RenderDrawLine(renderer, cx + x, cy + y, cx - x, cy + y)  # Q I, Q II
        sdl2.SDL_RenderDrawLine(renderer, cx + x, cy,     cx + x, cy - y)  # Q III
        sdl2.SDL_RenderDrawLine(renderer, cx - x, cy - y, cx,     cy - y)  # Q I

        radius = err
        if radius <= y:
            y += 1
            err += y * 2 + 1

        if (radius > x) or (err > y):
            x += 1
            err += x * 2 + 1
    
        if x >= 0: break

def _draw_ellipse(renderer, cx, cy, ar, br):
    # II. quadrant from bottom left to top right */
    cx, cy, ar, br = round(cx), round(cy), round(ar), round(br)
    x = -ar
    y = 0
    a2 = ar * ar
    b2 = br * br
    e2 = br
    dx = (1 + 2 * x) * e2 * e2
    dy = x * x
    err = dx + dy

    while True:
        sdl2.SDL_RenderDrawPoint(renderer, cx - x, cy + y)
        sdl2.SDL_RenderDrawPoint(renderer, cx + x, cy + y)
        sdl2.SDL_RenderDrawPoint(renderer, cx + x, cy - y)
        sdl2.SDL_RenderDrawPoint(renderer, cx - x, cy - y)

        e2 = 2 * err
        if e2 >= dx: # x step
            x += 1
            dx += 2 * b2
            err += dx
        if e2 <= dy: # y step
            y += 1
            dy += 2 * a2
            err += dy
    
        if x > 0: break

    # to early stop for flat ellipses with a = 1, finish tip of ellipse
    y += 1
    while y < br:
        sdl2.SDL_RenderDrawPoint(renderer, cx, cy + y)
        sdl2.SDL_RenderDrawPoint(renderer, cx, cy - y)
        y += 1

def _fill_ellipse(renderer, cx, cy, ar, br):
    # II. quadrant from bottom left to top right */
    cx, cy, ar, br = round(cx), round(cy), round(ar), round(br)
    x = -ar
    y = 0
    a2 = ar * ar
    b2 = br * br
    e2 = br
    dx = (1 + 2 * x) * e2 * e2
    dy = x * x
    err = dx + dy

    while True:
        sdl2.SDL_RenderDrawLine(renderer, cx + x, cy + y, cx - x, cy + y) # Q I, Q II
        sdl2.SDL_RenderDrawLine(renderer, cx + x, cy,     cx + x, cy - y) # Q III
        sdl2.SDL_RenderDrawLine(renderer, cx - x, cy - y, cx,     cy - y) # Q I

        e2 = 2 * err
        if e2 >= dx: # x step
            x += 1
            dx += 2 * b2
            err += dx
        if e2 <= dy: # y step
            y += 1
            dy += 2 * a2
            err += dy
    
        if x > 0: break

    # to early stop for flat ellipses with a = 1, finish tip of ellipse
    y += 1
    while y < br:
        sdl2.SDL_RenderDrawPoint(renderer, cx, cy + y, cx, cy - y)
        y += 1

def _draw_regular_polygon(renderer, n, cx, cy, r, rotation):
    # for inscribed regular polygon, the radius should be `Rcos(pi/n)`
    start = math.radians(rotation)
    delta = 2.0 * math.pi / float(n)

    x0 = px = r * math.cos(start) + cx
    y0 = py = r * math.sin(start) + cy

    for idx in range(1, n):
        theta = start + delta * float(idx)
        sx = r * math.cos(theta) + cx
        sy = r * math.sin(theta) + cy

        sdl2.SDL_RenderDrawLineF(renderer, px, py, sx, sy)
        px = sx
        py = sy

    if px != x0:
        sdl2.SDL_RenderDrawLineF(renderer, px, py, x0, y0)
    else:
        sdl2.SDL_RenderDrawPointF(renderer, cx, cy)

def _fill_regular_polygon(renderer, n, cx, cy, r, rotation):
    # for inscribed regular polygon, the radius should be `Rcos(pi/n)`
    start = math.radians(rotation)
    delta = 2.0 * math.pi / float(n)
    pts = []
    xmin = cx - r
    xmax = cx + r
    ymin = cy + r
    ymax = cy - r

    for idx in range(0, n):
        theta = start + delta * float(idx)
        sx = r * math.cos(theta) + cx
        sy = r * math.sin(theta) + cy

        pts.append(sdl2.SDL_FRect(sx, sy))

        if sy < ymin: ymin = sy
        if sy > ymax: ymax = sy
    
    pts.append(pts[0])

    y = ymin
    while y < ymax + 1.0:
        px = [0.0, 0.0]
        pcount = 0

        for i in range(0, n // 2 + 1):
            spt = pts[i]
            ept = pts[i + 1]

            px[pcount], py, t, _ = lines_intersection(spt.x, spt.y, ept.x, ept.y, xmin, y, xmax, y)
            if not math.isnan(t):
                if t >= 0.0 and t <= 1.0:
                    pcount += 1
            elif pcount == 0:
                px[0] = spt.x
                px[1] = ept.x
                pcount = 2
            
            if pcount == 2: break
 
            spt = pts[n - i]
            ept = pts[n - i - 1]
            
            px[pcount], py, t, _ = lines_intersection(spt.x, spt.y, ept.x, ept.y, xmin, y, xmax, y)
            if not math.isnan(t):
                if t >= 0.0 and t <= 1.0:
                    pcount += 1
            elif pcount == 0:
                px[0] = spt.x
                px[1] = ept.x
                pcount = 2

            if pcount == 2: break

        if pcount == 2:
            sdl2.SDL_RenderDrawLineF(renderer, px[0], y, px[1], y)
        elif n == 2:
            sdl2.SDL_RenderDrawPointF(renderer, px[0], py)
        elif n <= 1:
            sdl2.SDL_RenderDrawPointF(renderer, cx, cy)

        y += 1.0
