# MindPlus with microPython
# Football Shot

from cosmos import *
from random import randint

###############################################
class FootballShot(Cosmos):
    def __init__(self, fps):
        super(FootballShot, self).__init__(fps)    

    def load(self, width, height):
        self.ball = self.insert(Circlet(4, True))
        self.ball.set_border_strategy(BorderStrategy.BOUNCE)
        self.ball.set_speed(4, 45.0)

    def reflow(self, width, height):
        self.move_to(self.ball, (width * 0.5, height * 0.5), MatterAnchor.CC)
 