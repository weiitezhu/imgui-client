import os


def create_shader_files():
    if not os.path.exists("shaders"):
        os.makedirs("shaders")

    # 顶点着色器
    vertex_shader = """
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

    # 片段着色器
    fragment_shader = """
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

    # 光源顶点着色器
    light_vertex_shader = """
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

    # 光源片段着色器
    light_fragment_shader = """
    #version 330 core
    out vec4 FragColor;

    uniform vec3 lightColor;

    void main()
    {
        FragColor = vec4(lightColor, 1.0);
    }
    """

    # 写入文件
    with open("shaders/vertex.glsl", "w") as f:
        f.write(vertex_shader)

    with open("shaders/fragment.glsl", "w") as f:
        f.write(fragment_shader)

    with open("shaders/light_vertex.glsl", "w") as f:
        f.write(light_vertex_shader)

    with open("shaders/light_fragment.glsl", "w") as f:
        f.write(light_fragment_shader)
