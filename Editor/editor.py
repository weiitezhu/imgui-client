import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
import OpenGL.GL as gl

from Context.context import Context
from Stores.mainwindowStore import MainWindowStore
from Views.views import main_window


class Editor:

    def __init__(self):
        self.window = -1
        self.impl = None
        self.store = MainWindowStore()
        self.set_up_imgui()
        self.context = Context()

    def set_up_imgui(self):
        # 创建窗口
        window = glfw.create_window(1280, 720, "3D Model Designer", None, None)
        if not window:
            print("Failed to create GLFW window")
            glfw.terminate()
            return

        glfw.make_context_current(window)
        glfw.swap_interval(1)  # 启用 VSync

        # 初始化 ImGui
        imgui.create_context()
        impl = GlfwRenderer(window)
        self.window = window
        self.impl = impl

    def exec(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.impl.process_inputs()

            imgui.new_frame()

            # 渲染主界面
            main_window(self.store)

            imgui.render()
            gl.glClearColor(0.1, 0.1, 0.1, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            self.impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)

    def __del__(self):
        # 清理
        self.impl.shutdown()
        glfw.terminate()
