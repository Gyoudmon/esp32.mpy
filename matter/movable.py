from ..forward import *

import math

###################################################################################################
class IMovable(object):
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
        if isinstance(strategy, enum.Enum):
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
