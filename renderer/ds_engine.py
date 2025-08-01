import numpy as np
import OpenGL.GL as gl
from PIL import Image
import pyrr


class Shader:
    def __init__(self, vertex_path, fragment_path):
        # 加载着色器源码
        with open(vertex_path, 'r') as f:
            vertex_source = f.read()
        with open(fragment_path, 'r') as f:
            fragment_source = f.read()

        # 编译顶点着色器
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, vertex_source)
        gl.glCompileShader(vertex_shader)
        if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(vertex_shader).decode()
            raise RuntimeError(f"顶点着色器编译错误:\n{error}")

        # 编译片段着色器
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, fragment_source)
        gl.glCompileShader(fragment_shader)
        if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(fragment_shader).decode()
            raise RuntimeError(f"片段着色器编译错误:\n{error}")

        # 创建着色器程序
        self.program = gl.glCreateProgram()
        gl.glAttachShader(self.program, vertex_shader)
        gl.glAttachShader(self.program, fragment_shader)
        gl.glLinkProgram(self.program)
        if not gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS):
            error = gl.glGetProgramInfoLog(self.program).decode()
            raise RuntimeError(f"着色器程序链接错误:\n{error}")

        # 删除着色器对象
        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

    def use(self):
        gl.glUseProgram(self.program)

    def set_mat4(self, name, value):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniformMatrix4fv(loc, 1, gl.GL_FALSE, value)

    def set_vec3(self, name, value):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform3fv(loc, 1, value)

    def set_float(self, name, value):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1f(loc, value)

    def set_int(self, name, value):
        loc = gl.glGetUniformLocation(self.program, name)
        gl.glUniform1i(loc, value)


class Texture:
    def __init__(self, path, texture_type=gl.GL_TEXTURE_2D):
        self.texture_id = gl.glGenTextures(1)
        gl.glBindTexture(texture_type, self.texture_id)

        # 设置纹理参数
        gl.glTexParameteri(texture_type, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(texture_type, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(texture_type, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(texture_type, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # 加载图像
        try:
            image = Image.open(path)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = np.array(image, dtype=np.uint8)

            if image.mode == "RGB":
                format = gl.GL_RGB
            elif image.mode == "RGBA":
                format = gl.GL_RGBA
            else:
                raise ValueError(f"不支持的图像格式: {image.mode}")

            gl.glTexImage2D(texture_type, 0, format, image.width, image.height,
                            0, format, gl.GL_UNSIGNED_BYTE, img_data)
            gl.glGenerateMipmap(texture_type)
        except Exception as e:
            print(f"加载纹理失败: {path}, 错误: {e}")
            # 创建默认纹理
            default_data = np.zeros((64, 64, 3), dtype=np.uint8)
            default_data[::8, :] = [255, 0, 255]  # 棋盘格图案
            default_data[:, ::8] = [255, 0, 255]
            gl.glTexImage2D(texture_type, 0, gl.GL_RGB, 64, 64,
                            0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, default_data)
            gl.glGenerateMipmap(texture_type)

        gl.glBindTexture(texture_type, 0)

    def bind(self, unit, texture_type=gl.GL_TEXTURE_2D):
        gl.glActiveTexture(gl.GL_TEXTURE0 + unit)
        gl.glBindTexture(texture_type, self.texture_id)


class Camera:
    def __init__(self, position=[0.0, 0.0, 3.0], up=[0.0, 1.0, 0.0], yaw=-90.0, pitch=0.0):
        self.position = np.array(position, dtype=np.float32)
        self.world_up = np.array(up, dtype=np.float32)
        self.yaw = yaw
        self.pitch = pitch
        self.front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.movement_speed = 2.5
        self.mouse_sensitivity = 0.1
        self.zoom = 45.0
        self.update_camera_vectors()

    def update_camera_vectors(self):
        # 计算新的相机方向
        front = np.zeros(3, dtype=np.float32)
        front[0] = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        front[1] = np.sin(np.radians(self.pitch))
        front[2] = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        self.front = front / np.linalg.norm(front)

        # 计算右向量和上向量
        self.right = np.cross(self.front, self.world_up)
        self.right = self.right / np.linalg.norm(self.right)
        self.up = np.cross(self.right, self.front)
        self.up = self.up / np.linalg.norm(self.up)

    def get_view_matrix(self):
        return pyrr.matrix44.create_look_at(
            self.position,
            self.position + self.front,
            self.up
        )

    def process_keyboard(self, direction, delta_time):
        velocity = self.movement_speed * delta_time
        if direction == "FORWARD":
            self.position += self.front * velocity
        if direction == "BACKWARD":
            self.position -= self.front * velocity
        if direction == "LEFT":
            self.position -= self.right * velocity
        if direction == "RIGHT":
            self.position += self.right * velocity
        if direction == "UP":
            self.position += self.world_up * velocity
        if direction == "DOWN":
            self.position -= self.world_up * velocity

    def process_mouse_movement(self, xoffset, yoffset, constrain_pitch=True):
        xoffset *= self.mouse_sensitivity
        yoffset *= self.mouse_sensitivity

        self.yaw += xoffset
        self.pitch += yoffset

        if constrain_pitch:
            if self.pitch > 89.0:
                self.pitch = 89.0
            if self.pitch < -89.0:
                self.pitch = -89.0

        self.update_camera_vectors()

    def process_mouse_scroll(self, yoffset):
        self.zoom -= yoffset
        if self.zoom < 1.0:
            self.zoom = 1.0
        if self.zoom > 90.0:
            self.zoom = 90.0


class Model:
    def __init__(self):
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)
        self.textures = []
        self.indices_count = 0

    def load_cube(self):
        # 立方体顶点数据 (位置, 法线, 纹理坐标)
        vertices = np.array([
            # 前面
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 1.0,

            # 后面
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0,

            # 上面
            -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 1.0,
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0,

            # 下面
            -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 1.0,
            0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 1.0,
            0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 1.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 0.0,

            # 右面
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 1.0,

            # 左面
            -0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 0.0,
            -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0,
            -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 1.0,
        ], dtype=np.float32)

        # 立方体索引数据
        indices = np.array([
            0, 1, 2, 2, 3, 0,  # 前面
            4, 5, 6, 6, 7, 4,  # 后面
            8, 9, 10, 10, 11, 8,  # 上面
            12, 13, 14, 14, 15, 12,  # 下面
            16, 17, 18, 18, 19, 16,  # 右面
            20, 21, 22, 22, 23, 20  # 左面
        ], dtype=np.uint32)

        self.indices_count = len(indices)

        # 绑定VAO
        gl.glBindVertexArray(self.vao)

        # 顶点数据
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        # 索引数据
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

        # 位置属性
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * 4, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        # 法线属性
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * 4, gl.ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(1)

        # 纹理坐标属性
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8 * 4, gl.ctypes.c_void_p(6 * 4))
        gl.glEnableVertexAttribArray(2)

        # 解绑
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def draw(self, shader):
        # 绑定纹理
        for i, texture in enumerate(self.textures):
            texture.bind(i)
            shader.set_int(f"material.texture_diffuse{i}", i)

        # 绘制模型
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, self.indices_count, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)


class RenderEngine:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.camera_pos = np.array([0.0, 0.0, 3.0], dtype=np.float32)
        self.camera_front = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        self.camera_up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        self.light_pos = np.array([1.2, 1.0, 2.0], dtype=np.float32)
        self.light_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.background_color = (0.1, 0.1, 0.1, 1.0)
        self.light_intensity = 1.0
        self.rotation_speed = 0.5
        self.wireframe_mode = False
        self.framebuffer = None
        self.texture_id = None
        self.renderbuffer = None
        self.vao = 0
        self.vbo = 0
        self.ebo = 0
        self.shader = None
        self.light_shader = None
        self.cube_texture = None
        self.initialized = False

    def initialize(self):
        """初始化渲染引擎和OpenGL资源"""
        if self.initialized:
            return

        # 检查 OpenGL 版本
        print(f"OpenGL Version: {gl.glGetString(gl.GL_VERSION).decode()}")
        print(f"GLSL Version: {gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION).decode()}")

        # 检查帧缓冲支持
        if not gl.glGenFramebuffers:
            raise RuntimeError("Framebuffers not supported! Requires OpenGL 3.0+")

        # 创建帧缓冲对象
        self.framebuffer = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer)

        # 创建纹理附件
        self.texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, self.width, self.height,
                        0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
                                  gl.GL_TEXTURE_2D, self.texture_id, 0)

        # 创建渲染缓冲对象（深度和模板附件）
        self.renderbuffer = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.renderbuffer)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8,
                                 self.width, self.height)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_STENCIL_ATTACHMENT,
                                     gl.GL_RENDERBUFFER, self.renderbuffer)

        # 检查帧缓冲是否完整
        if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("帧缓冲不完整")

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        # 初始化OpenGL状态
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # 加载着色器
        self.shader = self.create_shader(self.get_vertex_shader(), self.get_fragment_shader())
        self.light_shader = self.create_shader(self.get_light_vertex_shader(), self.get_light_fragment_shader())

        # 加载纹理
        self.cube_texture = self.load_texture("container2.png")

        # 创建立方体几何
        self.create_cube_geometry()

        self.initialized = True

    def resize(self, width, height):
        """调整渲染尺寸"""
        if width <= 0 or height <= 0:
            return

        self.width = width
        self.height = height

        # 重新创建纹理附件
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture_id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, width, height,
                        0, gl.GL_RGB, gl.GL_UNSIGNED_BYTE, None)

        # 重新创建渲染缓冲
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.renderbuffer)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, width, height)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def render(self, time):
        """渲染场景到帧缓冲"""
        if not self.initialized:
            return

        # 绑定到帧缓冲
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.framebuffer)
        gl.glViewport(0, 0, self.width, self.height)

        # 清除缓冲
        gl.glClearColor(*self.background_color)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # 设置线框模式
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK,
                         gl.GL_LINE if self.wireframe_mode else gl.GL_FILL)

        # 创建视图和投影矩阵
        view = pyrr.matrix44.create_look_at(
            self.camera_pos,
            self.camera_pos + self.camera_front,
            self.camera_up
        )

        projection = pyrr.matrix44.create_perspective_projection(
            45.0, self.width / self.height, 0.1, 100.0
        )

        # 渲染主立方体
        gl.glUseProgram(self.shader)

        # 设置矩阵
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "view"),
            1, gl.GL_FALSE, view
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "projection"),
            1, gl.GL_FALSE, projection
        )

        # 模型矩阵（旋转）
        model = pyrr.matrix44.create_from_translation(np.array([0.0, 0.0, 0.0]))
        model = pyrr.matrix44.multiply(
            model,
            pyrr.matrix44.create_from_axis_rotation(
                np.array([0.5, 1.0, 0.0]),
                time * self.rotation_speed
            )
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.shader, "model"),
            1, gl.GL_FALSE, model
        )

        # 设置光照属性
        gl.glUniform3f(
            gl.glGetUniformLocation(self.shader, "light.position"),
            self.light_pos[0], self.light_pos[1], self.light_pos[2]
        )
        gl.glUniform3f(
            gl.glGetUniformLocation(self.shader, "light.ambient"),
            0.2 * self.light_intensity,
            0.2 * self.light_intensity,
            0.2 * self.light_intensity
        )
        gl.glUniform3f(
            gl.glGetUniformLocation(self.shader, "light.diffuse"),
            0.5 * self.light_intensity,
            0.5 * self.light_intensity,
            0.5 * self.light_intensity
        )
        gl.glUniform3f(
            gl.glGetUniformLocation(self.shader, "light.specular"),
            1.0 * self.light_intensity,
            1.0 * self.light_intensity,
            1.0 * self.light_intensity
        )

        # 设置材质属性
        gl.glUniform1f(
            gl.glGetUniformLocation(self.shader, "material.shininess"),
            32.0
        )

        # 绑定纹理
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.cube_texture)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader, "material.texture_diffuse1"), 0)

        # 绘制立方体
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)

        # 渲染光源立方体
        gl.glUseProgram(self.light_shader)

        # 设置矩阵
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.light_shader, "view"),
            1, gl.GL_FALSE, view
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.light_shader, "projection"),
            1, gl.GL_FALSE, projection
        )

        # 模型矩阵（缩放）
        model = pyrr.matrix44.create_from_translation(self.light_pos)
        model = pyrr.matrix44.multiply(
            model,
            pyrr.matrix44.create_from_scale(np.array([0.2, 0.2, 0.2]))
        )
        gl.glUniformMatrix4fv(
            gl.glGetUniformLocation(self.light_shader, "model"),
            1, gl.GL_FALSE, model
        )

        # 设置光源颜色
        gl.glUniform3f(
            gl.glGetUniformLocation(self.light_shader, "lightColor"),
            self.light_color[0] * self.light_intensity,
            self.light_color[1] * self.light_intensity,
            self.light_color[2] * self.light_intensity
        )

        # 绘制光源立方体
        gl.glBindVertexArray(self.vao)
        gl.glDrawElements(gl.GL_TRIANGLES, 36, gl.GL_UNSIGNED_INT, None)

        # 解绑
        gl.glBindVertexArray(0)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def create_cube_geometry(self):
        """创建立方体几何数据"""
        # 立方体顶点数据 (位置, 法线, 纹理坐标)
        vertices = np.array([
            # 前面
            -0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0,
            -0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 1.0,

            # 后面
            -0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0,
            -0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0,

            # 上面
            -0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0,
            0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 1.0, 1.0,
            -0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0,

            # 下面
            -0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 1.0,
            0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 1.0,
            0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 1.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 0.0,

            # 右面
            0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0,
            0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 1.0,

            # 左面
            -0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0,
            -0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 0.0,
            -0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0,
            -0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 1.0,
        ], dtype=np.float32)

        # 立方体索引数据
        indices = np.array([
            0, 1, 2, 2, 3, 0,  # 前面
            4, 5, 6, 6, 7, 4,  # 后面
            8, 9, 10, 10, 11, 8,  # 上面
            12, 13, 14, 14, 15, 12,  # 下面
            16, 17, 18, 18, 19, 16,  # 右面
            20, 21, 22, 22, 23, 20  # 左面
        ], dtype=np.uint32)

        # 创建VAO, VBO, EBO
        self.vao = gl.glGenVertexArrays(1)
        self.vbo = gl.glGenBuffers(1)
        self.ebo = gl.glGenBuffers(1)

        # 绑定VAO
        gl.glBindVertexArray(self.vao)

        # 顶点数据
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

        # 索引数据
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, gl.GL_STATIC_DRAW)

        # 位置属性
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * 4, gl.ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(0)

        # 法线属性
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, gl.GL_FALSE, 8 * 4, gl.ctypes.c_void_p(3 * 4))
        gl.glEnableVertexAttribArray(1)

        # 纹理坐标属性
        gl.glVertexAttribPointer(2, 2, gl.GL_FLOAT, gl.GL_FALSE, 8 * 4, gl.ctypes.c_void_p(6 * 4))
        gl.glEnableVertexAttribArray(2)

        # 解绑
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)

    def create_shader(self, vertex_source, fragment_source):
        """创建着色器程序"""
        # 编译顶点着色器
        vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(vertex_shader, vertex_source)
        gl.glCompileShader(vertex_shader)
        if not gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(vertex_shader).decode()
            raise RuntimeError(f"顶点着色器编译错误:\n{error}")

        # 编译片段着色器
        fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(fragment_shader, fragment_source)
        gl.glCompileShader(fragment_shader)
        if not gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS):
            error = gl.glGetShaderInfoLog(fragment_shader).decode()
            raise RuntimeError(f"片段着色器编译错误:\n{error}")

        # 创建着色器程序
        shader_program = gl.glCreateProgram()
        gl.glAttachShader(shader_program, vertex_shader)
        gl.glAttachShader(shader_program, fragment_shader)
        gl.glLinkProgram(shader_program)
        if not gl.glGetProgramiv(shader_program, gl.GL_LINK_STATUS):
            error = gl.glGetProgramInfoLog(shader_program).decode()
            raise RuntimeError(f"着色器程序链接错误:\n{error}")

        # 删除着色器对象
        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)

        return shader_program

    def load_texture(self, filename):
        """加载纹理"""
        # 尝试加载纹理，失败则创建默认纹理
        try:
            # 这里简化了纹理加载，实际应用中可能需要完整路径
            image = Image.open(filename)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = np.array(image, dtype=np.uint8)

            if image.mode == "RGB":
                format = gl.GL_RGB
            elif image.mode == "RGBA":
                format = gl.GL_RGBA
            else:
                raise ValueError(f"不支持的图像格式: {image.mode}")
        except:
            # 创建默认棋盘格纹理
            img_data = np.zeros((64, 64, 3), dtype=np.uint8)
            for y in range(64):
                for x in range(64):
                    if (x // 8 + y // 8) % 2 == 0:
                        img_data[y, x] = [255, 0, 255]  # 紫色
                    else:
                        img_data[y, x] = [0, 255, 255]  # 青色
            format = gl.GL_RGB

        # 创建纹理
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)

        # 设置纹理参数
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

        # 上传纹理数据
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, format,
                        img_data.shape[1], img_data.shape[0],
                        0, format, gl.GL_UNSIGNED_BYTE, img_data)
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D)

        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
        return texture_id

    def get_texture_id(self):
        """获取渲染纹理ID"""
        return self.texture_id

    def cleanup(self):
        """清理资源"""
        if not self.initialized:
            return

        gl.glDeleteFramebuffers(1, [self.framebuffer])
        gl.glDeleteTextures(1, [self.texture_id])
        gl.glDeleteRenderbuffers(1, [self.renderbuffer])
        gl.glDeleteVertexArrays(1, [self.vao])
        gl.glDeleteBuffers(1, [self.vbo])
        gl.glDeleteBuffers(1, [self.ebo])
        gl.glDeleteProgram(self.shader)
        gl.glDeleteProgram(self.light_shader)
        gl.glDeleteTextures(1, [self.cube_texture])

        self.initialized = False

    def get_vertex_shader(self):
        """返回顶点着色器源码"""
        return """
        #version 330 core
        layout (location = 0) in vec3 aPos;
        layout (location = 1) in vec3 aNormal;
        layout (location = 2) in vec2 aTexCoords;

        out vec3 FragPos;
        out vec3 Normal;
        out vec2 TexCoords;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main()
        {
            FragPos = vec3(model * vec4(aPos, 1.0));
            Normal = mat3(transpose(inverse(model))) * aNormal;  
            TexCoords = aTexCoords;

            gl_Position = projection * view * vec4(FragPos, 1.0);
        }
        """

    def get_fragment_shader(self):
        """返回片段着色器源码"""
        return """
        #version 330 core
        out vec4 FragColor;

        struct Material {
            sampler2D texture_diffuse1;
            float shininess;
        }; 

        struct Light {
            vec3 position;

            vec3 ambient;
            vec3 diffuse;
            vec3 specular;
        };

        in vec3 FragPos;
        in vec3 Normal;
        in vec2 TexCoords;

        uniform vec3 viewPos;
        uniform Material material;
        uniform Light light;

        void main()
        {
            // 环境光照
            vec3 ambient = light.ambient * texture(material.texture_diffuse1, TexCoords).rgb;

            // 漫反射 
            vec3 norm = normalize(Normal);
            vec3 lightDir = normalize(light.position - FragPos);
            float diff = max(dot(norm, lightDir), 0.0);
            vec3 diffuse = light.diffuse * diff * texture(material.texture_diffuse1, TexCoords).rgb;

            // 镜面反射
            vec3 viewDir = normalize(viewPos - FragPos);
            vec3 reflectDir = reflect(-lightDir, norm);  
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
            vec3 specular = light.specular * spec * vec3(1.0);  

            vec3 result = ambient + diffuse + specular;
            FragColor = vec4(result, 1.0);
        }
        """

    def get_light_vertex_shader(self):
        """返回光源顶点着色器源码"""
        return """
        #version 330 core
        layout (location = 0) in vec3 aPos;

        uniform mat4 model;
        uniform mat4 view;
        uniform mat4 projection;

        void main()
        {
            gl_Position = projection * view * model * vec4(aPos, 1.0);
        }
        """

    def get_light_fragment_shader(self):
        """返回光源片段着色器源码"""
        return """
        #version 330 core
        out vec4 FragColor;

        uniform vec3 lightColor;

        void main()
        {
            FragColor = vec4(lightColor, 1.0);
        }
        """

    def __del__(self):
        self.cleanup()
