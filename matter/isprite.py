from ..imatter import *
from .movable import *

###################################################################################################
class ISprite(IMatter, IMovable):
    def __init__(self):
        super(ISprite, self).__init__()
