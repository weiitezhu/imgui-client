import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer
import OpenGL.GL as gl

from Editor.context import Context
from Stores.mainwindowStore import MainWindowStore
from Views.ui_main_imgui import MainUI


class Editor:

    def __init__(self):
        self.window = -1
        self.impl = None
        self.store = MainWindowStore()
        self.set_up_imgui()
        self.context = Context()
        self.ui = MainUI(self)

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

    def on_mouse_left_button_down(self):
        """处理鼠标左键按下事件"""
        pass

    def on_mouse_left_button_up(self):
        """处理鼠标左键释放事件"""
        pass

    def on_mouse_right_button_down(self):
        """处理鼠标右键按下事件"""
        pass

    def on_mouse_right_button_up(self):
        """处理鼠标右键释放事件"""
        pass

    def on_mouse_middle_button_down(self):
        """处理鼠标中键按下事件"""
        pass

    def on_mouse_middle_button_up(self):
        """处理鼠标中键释放事件"""
        pass

    def on_mouse_move(self):
        """处理鼠标移动事件"""
        pass

    def on_mouse_wheel_scroll(self):
        """处理鼠标滚轮滚动事件"""
        pass

    def on_mouse_enter(self):
        """处理鼠标进入窗口事件"""
        pass

    def on_mouse_leave(self):
        """处理鼠标离开窗口事件"""
        pass

    def on_mouse_left_button_drag(self):
        """处理鼠标左键拖拽事件"""
        pass

    def on_mouse_right_button_drag(self):
        """处理鼠标右键拖拽事件"""
        pass

    def on_mouse_center_button_drag(self):
        """处理鼠标中键拖拽事件"""
        pass

    def is_mouse_hovering_over_area(self):
        """检查鼠标是否悬停在特定区域"""
        pass

    def exec(self):
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            self.impl.process_inputs()

            imgui.new_frame()
            # 渲染主界面
            # main_window(self.store)
            self.ui()

            imgui.render()
            gl.glClearColor(0.1, 0.1, 0.1, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
            self.impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)

    def __del__(self):
        # 清理
        self.impl.shutdown()
        glfw.terminate()
