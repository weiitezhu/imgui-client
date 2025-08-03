from Editor.editor import Editor
import imgui


class MainUI:

    def __init__(self, editor: Editor):
        self.editor = editor

    def __call__(self, *args, **kwargs):
        self.__draw()

    def __draw(self):
        # 设置主窗口样式
        imgui.set_next_window_position(0, 0)
        imgui.set_next_window_size(imgui.get_io().display_size.x, imgui.get_io().display_size.y)

        imgui.begin("3D Model Designer", flags=(
                imgui.WINDOW_MENU_BAR |
                imgui.WINDOW_NO_DECORATION |
                imgui.WINDOW_NO_MOVE |
                imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS
        ))

        # 菜单栏
        if imgui.begin_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("New")[0]:
                    pass  # 创建新项目
                if imgui.menu_item("Open")[0]:
                    pass  # 打开文件
                if imgui.menu_item("Save")[0]:
                    pass  # 保存文件
                if imgui.menu_item("Save As...")[0]:
                    pass  # 另存为
                imgui.separator()
                if imgui.menu_item("Exit")[0]:
                    pass  # 退出应用
                imgui.end_menu()

            if imgui.begin_menu("Edit"):
                if imgui.menu_item("Undo", "Ctrl+Z")[0]:
                    pass  # 撤销操作
                if imgui.menu_item("Redo", "Ctrl+Y")[0]:
                    pass  # 重做操作
                imgui.separator()
                if imgui.menu_item("Cut", "Ctrl+X")[0]:
                    pass  # 剪切
                if imgui.menu_item("Copy", "Ctrl+C")[0]:
                    pass  # 复制
                if imgui.menu_item("Paste", "Ctrl+V")[0]:
                    pass  # 粘贴
                imgui.end_menu()

            if imgui.begin_menu("View"):
                if imgui.menu_item("Reset View")[0]:
                    pass  # 重置视图
                if imgui.menu_item("Wireframe")[0]:
                    pass  # 线框模式
                imgui.end_menu()

            if imgui.begin_menu("Help"):
                if imgui.menu_item("About")[0]:
                    pass  # 关于
                imgui.end_menu()

            imgui.end_menu_bar()

        # 主要区域布局
        menu_height = imgui.get_frame_height_with_spacing()
        work_pos = (0, menu_height)
        work_size = (
            imgui.get_io().display_size.x,
            imgui.get_io().display_size.y - menu_height - 24  # 24是状态栏高度
        )

        # 分割窗口
        imgui.set_cursor_pos(work_pos)
        imgui.begin_child("Workspace", work_size[0], work_size[1], flags=imgui.WINDOW_NO_SCROLLBAR)

        # 左侧面板
        self.__left_panel()

        # 中间视图区域
        imgui.same_line()
        self.__view_port()

        # 右侧面板
        imgui.same_line()
        self.__right_panel()

        imgui.end_child()
        imgui.end()

        # 渲染状态栏
        self.__status_bar()

    def __left_panel(self):
        pass

    def __right_panel(self):
        pass

    def __status_bar(self):
        pass

    def __view_port(self):
        pass
