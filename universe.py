# MindPlus with microPython

from mpython import *
from machine import Timer as SysTimer

###############################################
class Timer(object):
  _id = 0
  
  def __init__(self, interval):
    Timer._id += 1
    self._self = SysTimer(Timer._id)
    self._self.init(period=interval, mode=SysTimer.PERIODIC,
                      callback= lambda a: self.on_tick(a))
    
  def on_tick(self, _):
    pass

class PhysicsWatcher(Timer):
  def __init__(self, target):
    self.target = target
    super(PhysicsWatcher, self).__init__(100)
    
  def on_tick(self, _):
    datum = light.read()
    if datum > 0: self.on_light(datum, datum / 4095)
    
    datum = sound.read()
    if datum > 0: self.on_sound(datum, datum / 4095)
    
  def on_light(self, value, percentage):
    self.target.on_light(value, percentage)
    
  def on_sound(self, value, percentage):
    self.target.on_sound(value, percentage)
    
class TouchpadWatcher(Timer):
  def __init__(self, threshold, target):
    self.target = target
    
    super(TouchpadWatcher, self).__init__(100)
    
    self._threshold = { 'P': threshold, 'Y': threshold, 'T': threshold, 'H': threshold, 'O': threshold, 'N': threshold }
    
  def on_tick(self, _):
    try:
      touchPad_P.read()
    except:
      return
  
    self._dispatch(touchPad_P.read(), 'P', 1)
    self._dispatch(touchPad_Y.read(), 'Y', 2)
    self._dispatch(touchPad_T.read(), 'T', 3)
    self._dispatch(touchPad_H.read(), 'H', 4)
    self._dispatch(touchPad_O.read(), 'O', 5)
    self._dispatch(touchPad_N.read(), 'N', 6)
    
  def on_touchpad_key(self, keyname, key_idx, pressed):
    self.target.on_touchpad_key(keyname, key_idx, pressed)
  
  def _dispatch(self, read_datum, keyname, idx):
    if read_datum < self._threshold[keyname]:
      self.on_touchpad_key(keyname, idx, True)
    else:
      self.on_touchpad_key(keyname, idx, False)
      
class ButtonWatcher(object):
  def __init__(self, target):
    self.target = target
    button_a.irq(trigger=Pin.IRQ_FALLING,
                  handler= lambda a: self._ugly_python(button_a.value(), button_b.value(), 'A'))
    button_b.irq(trigger=Pin.IRQ_FALLING,
                  handler= lambda a: self._ugly_python(button_b.value(), button_a.value(), 'B'))
    
  def on_button_key(self, who, pressed):
    self.target.on_button_key(who, pressed)

  def _ugly_python(self, value, the_other_value, who):
    if value == the_other_value:
      if value == 0:
        self.on_button_key('C', True)
      else:
        self.on_button_key('C', False)
    elif value == 0:
        self.on_button_key(who, True)
    else:
        self.on_button_key(who, False)

###############################################################################
class Universe(Timer):
# public
    def __init__(self, interval, width = 128, height = 64):
        """ 构造函数，在创建游戏世界时自动调用 """
        
        # The constructors of base classes must be invoked explicitly
        # even if there is only one that has no argument
        super(Universe, self).__init__(interval)
        
        # Please search "Python sequence unpacking"(序列解包)
        self.__window_width, self.__window_height = 128, 64
        self.__count, self.__interval, self.__uptime = 0, interval, 0
        self.__update_sequence_depth = 0
        self.__update_is_needed = False
        self.__button_watcher = None
        self.__touchpad_watcher = None
        self.__physics_watcher = None

        # Python doesn't need two-step initialization as C++ does
        self.construct()

    def __getattr__(self, name):
        def method(*args): pass
        return method

# public
    def construct(self):
        """ 给游戏世界一个解析命令行参数的机会，默认什么都不做 """
        pass

    def reflow(self, width, height):
        """ 排列可视化元素，在合适的时候自动调用，默认什么都不做 """
        pass

    def update(self, interval, count, uptime):
        """ 更新游戏世界，定时器到期时自动调用，默认什么都不做 """
        pass

    def draw(self, x, y, width, height):
        """ 绘制游戏世界，在合适的时候自动调用，默认什么都不做 """
        pass

    def can_exit(self):
        """ 告诉游戏主循环，是否游戏已经结束可以退出了，默认永久运行 """
        return False

    def big_bang(self):
        """ 宇宙大爆炸，开启游戏主循环，返回游戏运行时间 """

        self.__touchpad_watcher = TouchpadWatcher(400, self)
        self.__button_watcher = ButtonWatcher(self)
        self.__physics_watcher = PhysicsWatcher(self)
        
        self.__window_width, self.__window_height = self.get_window_size()
        self.begin_update_sequence()
        self._on_big_bang(self.__window_width, self.__window_height)
        self.reflow(self.__window_width, self.__window_height)
        self.notify_updated()
        self.end_update_sequence()

# public
    def get_window_size(self):
        return 128, 64

    def get_extent(self):
        return self.get_window_size()

    def refresh(self):
        oled.fill(0)
        self.draw(0, 0, self.__width, self.__height)
        oled.show()        

    def on_tick(self, _):
        if self.__button_watcher:
            self.__count += 1
            self.__uptime += self.__interval
            self._on_elapse(self.__interval, self.__count, self.__uptime)

# public
    def begin_update_sequence(self):
        self.__update_sequence_depth += 1

    def is_in_update_sequence(self):
        return self.__update_sequence_depth > 0

    def end_update_sequence(self):
        self.__update_sequence_depth -= 1

        if self.__update_sequence_depth < 1:
            self.__update_sequence_depth = 0

            if self.should_update():
                self.refresh()
                self.__update_is_needed = False

    def should_update(self):
        return self.__update_is_needed

    def notify_updated(self):
        if self.is_in_update_sequence():
            self.__update_is_needed = True
        else:
            self.refresh()
            self.__update_is_needed = False

# public
    # 响应按钮事件，并按需触发按下、松开事件
    def on_button_key(self, which, pressed):
        pass

    # 响应按钮事件，并按需触发按下、松开事件
    def on_touchpad_key(self, which, index, pressed):
        pass

    # 响应亮度变化事件
    def on_light(self, value, percentage):
        pass
    
    # 响应音量变化事件
    def on_sound(self, value, percentage):
        pass

# protected
    # 大爆炸之前最后的初始化宇宙机会，默认什么都不做
    def _on_big_bang(self, width, height): pass

    # 响应定时器事件，刷新游戏世界
    def _on_elapse(self, interval, count, uptime):
        """ 响应定时器事件，刷新游戏世界 """
        self.update(interval, count, uptime)
        self.notify_updated()
