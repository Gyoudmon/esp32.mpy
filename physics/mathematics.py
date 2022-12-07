import math

###################################################################################################
def radians_to_degrees(radians):
    return math.degrees(radians)

def degrees_to_radians(degrees):
    return math.radians(degrees)

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
