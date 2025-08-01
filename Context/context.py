from enum import Enum, auto
from threading import Lock

from Utiles.signal import SignalMeta
from renderer.ds_engine import RenderEngine

class AppModeEnum(Enum):
    EDITOR = 0
    COMMAND = auto()
    VIEW_PORT = auto()
    OPERATE = auto()


class RenderModeEnum(Enum):
    NONE = 0
    PYSIDE = auto()
    OPENGL = auto()
    OTHER = auto()


# 单例类
class Context(metaclass=SignalMeta):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render_mode = RenderModeEnum.OPENGL
        self.app_mode = AppModeEnum.EDITOR
        self.render = RenderEngine()
        self.render.initialize()

    def switch_app_mode(self, mode: AppModeEnum):
        self.app_mode = mode

    def switch_render_mode(self, mode: RenderModeEnum):
        self.render_mode = mode

    def command_event(self):
        pass

    def view_port_event(self):
        pass

    def operate_event(self):
        pass
