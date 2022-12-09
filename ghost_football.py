# Ghosts' Football Match

from cosmos import *
from random import randint

###############################################
class FootballShot(Cosmos):
    def __init__(self, fps):
        super(FootballShot, self).__init__(fps)
        self.__r_goal = 0
        self.__l_goal = 0

    def load(self, width, height):
        self.l_goal = self.insert(Labellet("0"))
        self.r_goal = self.insert(Labellet("0"))
        self.midline = self.insert(VLinelet(height))
        self.circle = self.insert(Circlet(9.15 / 105.0 * width, False))
        self.l_door = self.insert(VLinelet(7.32 / 68.0 * height))
        self.r_door = self.insert(VLinelet(7.32 / 68.0 * height))
        self.ball = self.insert(Circlet(2, True))
        
        self.__startover()

    def reflow(self, width, height):
        cx = width * 0.5
        cy = height * 0.5

        self.move_to(self.midline, (cx, cy), MatterAnchor.CC)
        self.move_to(self.circle, (cx, cy), MatterAnchor.CC)
        self.move_to(self.l_door, (0.0, cy), MatterAnchor.LC)
        self.move_to(self.r_door, (width, cy), MatterAnchor.RC)
        self.move_to(self.l_goal, (0.0, 0.0), MatterAnchor.LT)
        self.move_to(self.r_goal, (width, 1.0), MatterAnchor.RT)

    def update(self, interval, count, uptime):
        width, height = self.get_extent()

        lx, y = self.get_matter_location(self.ball, MatterAnchor.LC)
        rx, y = self.get_matter_location(self.ball, MatterAnchor.RC)

        if lx == 0.0:
            _, door_ty = self.get_matter_location(self.l_door, MatterAnchor.CT)
            _, door_by = self.get_matter_location(self.l_door, MatterAnchor.CB)
            if flin(door_ty, y, door_by):
                self.__l_goal += 1
                self.l_goal.set_text(self.__l_goal, MatterAnchor.LT)
                self.move_to(self.ball, (width * 0.5, height * 0.5), MatterAnchor.CC)
            else:
                self.__ball_move()
        elif rx == width:
            _, door_ty = self.get_matter_location(self.r_door, MatterAnchor.CT)
            _, door_by = self.get_matter_location(self.r_door, MatterAnchor.CB)
            if flin(door_ty, y, door_by):
                self.__r_goal += 1
                self.r_goal.set_text(self.__r_goal, MatterAnchor.RT)
                self.move_to(self.ball, (width * 0.5, height * 0.5), MatterAnchor.CC)
            else:
                self.__ball_move()
        else:
            self.__ball_move()

        self.notify_updated()

    def __startover(self):
        width, height = self.get_extent()
        cx, cy = width * 0.5, height * 0.5

        self.move_to(self.ball, (cx, cy), MatterAnchor.CC)
        self.ball.set_border_strategy(BorderStrategy.STOP)

    def __ball_move(self):
        roll, pitch = self.get_roll_pitch_angle()
        self.ball.set_speed(2.0, math.atan2(pitch, roll), True)
        
###################################################################################################
if __name__ == "__main__":
    universe = FootballShot(24)
    universe.big_bang()
