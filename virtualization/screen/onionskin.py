from ..iscreen import *

###############################################################
class OnionSkin(IScreen):
    def __init__(self, display):
        self.__display = display

    def display(self):
        return self.__display

    def get_extent(self):
        return self.__display.get_extent()
        
    def refresh(self):
        self.__display.refresh()

    def begin_update_sequence(self):
        self.__display.begin_update_sequence()

    def is_in_update_sequence(self):
        return self.__display.is_in_update_sequence()

    def end_update_sequence(self):
        self.__display.end_update_sequence()

    def should_update(self):
        return self.__display.should_update()
    
    def notify_updated(self):
        return self.__display.notify_updated()

    def log_message(self, fgc, message):
        self.__display.log_message(fgc, message)

    def start_input_text(self, prompt):
        self.__display.start_input_text(prompt)
