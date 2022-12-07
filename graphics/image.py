import os
import sdl2
import sdl2.sdlimage as sdlimg

from .geometry import *
from .colorspace import *

###################################################################################################
def game_blank_image(width, height, alpha_color_key = 0xFFFFFF):
    surface = sdl2.SDL_CreateRGBSurface(0, round(width), round(height), 32, 0, 0, 0, 0)
    r, g, b = RGB_FromHexadecimal(alpha_color_key)
    sdl2.SDL_SetColorKey(surface, 1, sdl2.SDL_MapRGB(surface.contents.format, r, g, b))
    
    return surface

def game_load_image(file):
    return sdlimg.IMG_Load(file.encode("utf-8"))

def game_unload_image(image):
    sdl2.SDL_FreeSurface(image)

def game_draw_image(renderer, image, x, y):
    game_render_surface(renderer, image, (x, y))
    
def game_draw_image(renderer, file, x, y):
    image = game_load_image(file)

    if not image:
        game_draw_image(renderer, image, x, y)
        game_unload_image(image)

def game_draw_image(renderer, image, x, y, width, height):
    if image.w == width and image.h == height:
        game_render_surface(renderer, image, (x, y))
    else:
        region = sdlimg.SDL_Rect(round(x), round(y), round(width), round(height))

        if  width <= 0: region.w = image.w
        if height <= 0: region.h = image.h
        
        game_render_surface(renderer, image, region)

def game_draw_image(renderer, file, x, y, width, height):
    image = game_load_image(file)

    if not image:
        game_draw_image(renderer, image, x, y, width, height)
        game_unload_image(image)

###################################################################################################
def game_save_image(png, pname):
    okay = False

    if png:
        os.makedirs(os.path.dirname(pname), exist_ok = True)
        if sdlimg.IMG_SavePNG(png, pname.encode('utf-8')) == 0:
            okay = True

    return okay
