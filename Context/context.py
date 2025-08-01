from threading import Lock


# 单例类
class Context:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            with Lock():
                if cls.__instance is None:
                    cls.__instance = super().__new__(*args, **kwargs)

        return cls.__instance

    def __init__(self):
        pass

    def command_event(self):
        pass

    def view_port_event(self):
        pass

    def operate_event(self):
        pass
