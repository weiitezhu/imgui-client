# UI 事件分发
import time

from Context.context import Context, AppModeEnum, RenderModeEnum
import imgui
from Stores.mainwindowStore import MainWindowStore

start_time = time.time()

def main_window(store: MainWindowStore):
    context = Context()

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
    if context.app_mode == AppModeEnum.EDITOR:
        left_panel()

    # 中间视图区域
    imgui.same_line()
    view_port()

    # 右侧面板
    imgui.same_line()
    right_panel()

    imgui.end_child()
    imgui.end()

    # 渲染状态栏
    status_bar()


render_left_panel_selected_tool = 0
render_left_panel_selected_material = 0


def left_panel():
    imgui.begin_child("LeftPanel", 200, 0, True)

    # 工具选择
    if imgui.collapsing_header("Tools", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        selected_tool = getattr(left_panel, 'selected_tool', 0)
        tools = ["Select", "Move", "Rotate", "Scale", "Vertex Edit"]

        for i, tool in enumerate(tools):
            clicked, selected = imgui.selectable(tool, selected_tool == i)
            if clicked:
                left_panel.selected_tool = i
            if selected_tool == i:
                imgui.set_item_default_focus()

    # 对象层级结构
    if imgui.collapsing_header("Hierarchy", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        # 模拟对象树
        scene_node_open = imgui.tree_node("Scene")
        if scene_node_open:
            # 使用 TreeNodeEx flags
            model_node_open = imgui.tree_node("Model##leaf", flags=imgui.TREE_NODE_LEAF)
            if model_node_open:
                imgui.bullet_text("Mesh Renderer")
                imgui.bullet_text("Material")
                imgui.tree_pop()  # 对应 Model 的 tree_node

            light_node_open = imgui.tree_node("Light##leaf", flags=imgui.TREE_NODE_LEAF)
            if light_node_open:
                imgui.bullet_text("Point Light")
                imgui.tree_pop()  # 对应 Light 的 tree_node

            imgui.tree_pop()  # 对应 Scene 的 tree_node

    # 材质库
    if imgui.collapsing_header("Materials", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        selected_material = getattr(left_panel, 'selected_material', 0)
        materials = ["Default", "Metal", "Wood", "Glass", "Plastic"]

        for i, material in enumerate(materials):
            clicked, selected = imgui.selectable(material, selected_material == i)
            if clicked:
                left_panel.selected_material = i
            if selected_material == i:
                imgui.set_item_default_focus()

        imgui.spacing()
        if imgui.button("New Material"):
            pass  # 创建新材质

    imgui.end_child()


def right_panel():
    imgui.begin_child("RightPanel", 250, 0, True)

    # 变换属性
    if imgui.collapsing_header("Transform", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        position = getattr(right_panel, 'position', [0.0, 0.0, 0.0])
        rotation = getattr(right_panel, 'rotation', [0.0, 0.0, 0.0])
        scale = getattr(right_panel, 'scale', [1.0, 1.0, 1.0])

        imgui.text("Position")
        changed, position = imgui.drag_float3("##Position", *position, 0.1)
        if changed:
            right_panel.position = list(position)

        imgui.spacing()
        imgui.text("Rotation")
        changed, rotation = imgui.drag_float3("##Rotation", *rotation, 1.0)
        if changed:
            right_panel.rotation = list(rotation)

        imgui.spacing()
        imgui.text("Scale")
        changed, scale = imgui.drag_float3("##Scale", *scale, 0.1)
        if changed:
            right_panel.scale = list(scale)

    # 材质属性
    if imgui.collapsing_header("Material", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        color = getattr(right_panel, 'color', [1.0, 1.0, 1.0])
        changed, color = imgui.color_edit3("Color", *color)
        if changed:
            right_panel.color = list(color)

        metallic = getattr(right_panel, 'metallic', 0.0)
        changed, metallic = imgui.slider_float("Metallic", metallic, 0.0, 1.0)
        if changed:
            right_panel.metallic = metallic

        roughness = getattr(right_panel, 'roughness', 0.5)
        changed, roughness = imgui.slider_float("Roughness", roughness, 0.0, 1.0)
        if changed:
            right_panel.roughness = roughness

        opacity = getattr(right_panel, 'opacity', 1.0)
        changed, opacity = imgui.slider_float("Opacity", opacity, 0.0, 1.0)
        if changed:
            right_panel.opacity = opacity

    # 渲染设置
    if imgui.collapsing_header("Rendering", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        wireframe = getattr(right_panel, 'wireframe', False)
        changed, wireframe = imgui.checkbox("Wireframe", wireframe)
        if changed:
            right_panel.wireframe = wireframe

        normals = getattr(right_panel, 'normals', False)
        changed, normals = imgui.checkbox("Show Normals", normals)
        if changed:
            right_panel.normals = normals

        shading_mode = getattr(right_panel, 'shading_mode', 0)
        shading_modes = ["Solid", "Lit", "Unlit"]
        changed, shading_mode = imgui.combo("Shading", shading_mode, shading_modes)
        if changed:
            right_panel.shading_mode = shading_mode

        backface_culling = getattr(right_panel, 'backface_culling', True)
        changed, backface_culling = imgui.checkbox("Backface Culling", backface_culling)
        if changed:
            right_panel.backface_culling = backface_culling

    # 性能信息
    if imgui.collapsing_header("Performance", flags=imgui.TREE_NODE_DEFAULT_OPEN):
        imgui.spacing()

        io = imgui.get_io()
        imgui.text(f"FPS: {io.framerate:.1f}")
        imgui.text(f"Frame Time: {1000.0 / io.framerate:.2f} ms")
        imgui.text("Vertices: 1024")  # 示例数据
        imgui.text("Triangles: 512")  # 示例数据

        render_time = getattr(right_panel, 'render_time', 5.3)
        imgui.text(f"Render Time: {render_time:.2f} ms")

    imgui.end_child()


def status_bar():
    io = imgui.get_io()
    status_bar_size = (io.display_size.x, 24)
    
    # 设置状态栏位置在窗口底部
    imgui.set_cursor_pos((0, io.display_size.y - status_bar_size[1]))
    
    # 使用 imgui.begin() 创建一个固定的底部状态栏，而不是可移动的子窗口
    imgui.begin("StatusBar", flags=(
        imgui.WINDOW_NO_TITLE_BAR |
        imgui.WINDOW_NO_RESIZE |
        imgui.WINDOW_NO_MOVE |
        imgui.WINDOW_NO_COLLAPSE |
        imgui.WINDOW_NO_NAV |
        imgui.WINDOW_NO_SCROLLBAR |
        imgui.WINDOW_NO_SCROLL_WITH_MOUSE
    ))
    
    # 设置窗口位置和大小
    imgui.set_window_position(0, io.display_size.y - status_bar_size[1])
    imgui.set_window_size(status_bar_size[0], status_bar_size[1])
    
    # 状态栏背景
    draw_list = imgui.get_window_draw_list()
    cursor_pos = imgui.get_cursor_screen_position()
    draw_list.add_rect_filled(
        cursor_pos[0], cursor_pos[1],
        cursor_pos[0] + status_bar_size[0], cursor_pos[1] + status_bar_size[1],
        imgui.get_color_u32_rgba(0.15, 0.15, 0.15, 1.0)
    )
    
    # 文本内容
    imgui.set_cursor_pos_y(4)
    imgui.text("Ready")
    imgui.same_line()
    
    # 显示当前工具
    available_width = imgui.get_content_region_available_width()
    imgui.set_cursor_pos_x(available_width - 200)
    imgui.text("Tool: Select")
    imgui.same_line()
    
    # 显示坐标系
    imgui.set_cursor_pos_x(available_width - 100)
    coordinate_systems = ["Local", "World"]
    current_coord = getattr(status_bar, 'current_coord', 0)
    changed, current_coord = imgui.combo("##CoordSystem", current_coord, coordinate_systems)
    if changed:
        status_bar.current_coord = current_coord
    
    imgui.end()


render_viewport_current_view = 0


def view_port():
    context = Context()

    global render_viewport_current_view
    available_x = imgui.get_content_region_available_width()
    imgui.begin_child("Viewport", available_x - 250, 0, True)

    # 视口标题
    imgui.text("Viewport")
    imgui.same_line(imgui.get_content_region_available_width() - 120)

    # 视图模式选择
    view_modes = ["Edit", "Command", "ViewPort", "OPERATE"]
    current_view = render_viewport_current_view
    changed, current_view = imgui.combo("##ViewMode", current_view, view_modes)
    if changed:
        render_viewport_current_view = current_view
        if current_view == 0:
            context.switch_app_mode(AppModeEnum.EDITOR)
        elif current_view == 1:
            context.switch_app_mode(AppModeEnum.COMMAND)
        elif current_view == 2:
            context.switch_app_mode(AppModeEnum.VIEW_PORT)
        elif current_view == 3:
            context.switch_app_mode(AppModeEnum.OPERATE)

    # 3D视图区域
    if context.render_mode == RenderModeEnum.NONE:

        viewport_size = imgui.get_content_region_available()
        viewport_pos = imgui.get_cursor_screen_position()

        # 这里应该渲染3D场景到纹理，然后显示纹理
        # 示例中使用占位符
        draw_list = imgui.get_window_draw_list()
        draw_list.add_rect_filled(
            viewport_pos[0], viewport_pos[1],
            viewport_pos[0] + viewport_size[0], viewport_pos[1] + viewport_size[1],
            imgui.get_color_u32_rgba(0.2, 0.2, 0.2, 1.0)
        )

        # 绘制简单的3D坐标轴指示器
        axis_size = 80.0
        axis_pos_x = viewport_pos[0] + 20
        axis_pos_y = viewport_pos[1] + viewport_size[1] - 20

        # X轴 (红色)
        draw_list.add_line(
            axis_pos_x, axis_pos_y,
            axis_pos_x + axis_size, axis_pos_y,
            imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 1.0), 2.0
        )
        draw_list.add_text(
            axis_pos_x + axis_size - 10, axis_pos_y - 10,
            imgui.get_color_u32_rgba(1.0, 0.0, 0.0, 1.0), "X"
        )

        # Y轴 (绿色)
        draw_list.add_line(
            axis_pos_x, axis_pos_y,
            axis_pos_x, axis_pos_y - axis_size,
            imgui.get_color_u32_rgba(0.0, 1.0, 0.0, 1.0), 2.0
        )
        draw_list.add_text(
            axis_pos_x - 10, axis_pos_y - axis_size,
            imgui.get_color_u32_rgba(0.0, 1.0, 0.0, 1.0), "Y"
        )

        # Z轴 (蓝色)
        draw_list.add_line(
            axis_pos_x, axis_pos_y,
            axis_pos_x + axis_size * 0.7, axis_pos_y - axis_size * 0.7,
            imgui.get_color_u32_rgba(0.0, 0.0, 1.0, 1.0), 2.0
        )
        draw_list.add_text(
            axis_pos_x + axis_size * 0.7 - 10, axis_pos_y - axis_size * 0.7 - 10,
            imgui.get_color_u32_rgba(0.0, 0.0, 1.0, 1.0), "Z"
        )

        # 状态信息
        cursor_y = viewport_size[1] - 20
        imgui.set_cursor_pos((10, cursor_y))
        imgui.text("Position: (0.0, 0.0, 0.0)")
        imgui.same_line()
        imgui.text("Rotation: (0.0, 0.0, 0.0)")
    else:
        # 使用 OpenGL 渲染器
        render = context.render
        viewport_size = imgui.get_content_region_available()

        # 初始化渲染器
        render.resize(int(viewport_size[0]), int(viewport_size[1]))
        # 设置背景色
        # render.set_background_color(0.2, 0.2, 0.2)
        # 渲染场景
        current_time = time.time() - start_time
        render.render(current_time)

        # 在ImGui窗口中显示渲染结果
        imgui.image(
            render.get_texture_id(),
            int(viewport_size[0]), int(viewport_size[1]),
            (0, 1), (1, 0)  # 翻转Y轴
        )
    imgui.end_child()

# def main():
#     import imgui
#     from imgui.integrations.glfw import GlfwRenderer
#     import OpenGL.GL as gl
#     import glfw
#     # 初始化 GLFW
#     if not glfw.init():
#         print("Failed to initialize GLFW")
#         return
#
#     # OpenGL 版本设置
#     glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
#     glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
#     glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
#
#     # 创建窗口
#     window = glfw.create_window(1280, 720, "3D Model Designer", None, None)
#     if not window:
#         print("Failed to create GLFW window")
#         glfw.terminate()
#         return
#
#     glfw.make_context_current(window)
#     glfw.swap_interval(1)  # 启用 VSync
#
#     # 初始化 ImGui
#     imgui.create_context()
#     impl = GlfwRenderer(window)
#
#     # 主循环
#     while not glfw.window_should_close(window):
#         glfw.poll_events()
#         impl.process_inputs()
#
#         imgui.new_frame()
#
#         # 渲染主界面
#         main_window()
#
#         imgui.render()
#         gl.glClearColor(0.1, 0.1, 0.1, 1.0)
#         gl.glClear(gl.GL_COLOR_BUFFER_BIT)
#         impl.render(imgui.get_draw_data())
#         glfw.swap_buffers(window)
#
#     # 清理
#     impl.shutdown()
#     glfw.terminate()
#
#
# if __name__ == "__main__":
#     main()
