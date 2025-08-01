# main.py
import glfw
from Editor.editor import Editor


def main():
    # 初始化 GLFW
    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    # OpenGL 版本设置
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    e = Editor()
    e.exec()


if __name__ == "__main__":
    main()
