"""Experiment 9: OpenGL program using vertex and fragment shaders."""

import ctypes
import math

import glfw
from OpenGL.GL import *


WIDTH = 800
HEIGHT = 600
TITLE = "Vertex and Fragment Shaders"
ROTATION_SPEED = 45
MODE_NAMES = ["RGB interpolation", "Pulsing brightness", "Grayscale", "Inverted colours"]


VERTEX_SHADER_SOURCE = """
#version 330 core
layout (location = 0) in vec2 position;
layout (location = 1) in vec3 color;

uniform mat4 transform;

out vec3 vertexColor;

void main()
{
    gl_Position = transform * vec4(position, 0.0, 1.0);
    vertexColor = color;
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core
in vec3 vertexColor;
out vec4 fragmentColor;

uniform float time;
uniform int mode;

void main()
{
    vec3 color = vertexColor;

    if (mode == 1) {
        color *= 0.6 + 0.4 * sin(time * 3.0);
    } else if (mode == 2) {
        color = vec3(dot(color, vec3(0.299, 0.587, 0.114)));
    } else if (mode == 3) {
        color = vec3(1.0) - color;
    }

    fragmentColor = vec4(color, 1.0);
}
"""


def rotation_matrix(angle_in_degrees):
    angle = math.radians(angle_in_degrees)
    cos_value = math.cos(angle)
    sin_value = math.sin(angle)

    return [
        [cos_value, -sin_value, 0, 0],
        [sin_value, cos_value, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]


def scaling_matrix(sx, sy):
    return [
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]


def multiply_matrices(a, b):
    result = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    for row in range(4):
        for column in range(4):
            total = 0

            for k in range(4):
                total += a[row][k] * b[k][column]

            result[row][column] = total

    return result


def aspect_matrix(width, height):
    # Squashes the longer screen axis so the triangle keeps its shape in any window size
    if width >= height:
        return scaling_matrix(height / width, 1)

    return scaling_matrix(1, width / height)


def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error_message = glGetShaderInfoLog(shader).decode("utf-8")
        raise RuntimeError(f"Shader compilation failed: {error_message}")

    return shader


def create_shader_program():
    vertex_shader = compile_shader(VERTEX_SHADER_SOURCE, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(FRAGMENT_SHADER_SOURCE, GL_FRAGMENT_SHADER)

    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)

    if not glGetProgramiv(shader_program, GL_LINK_STATUS):
        error_message = glGetProgramInfoLog(shader_program).decode("utf-8")
        raise RuntimeError(f"Shader linking failed: {error_message}")

    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return shader_program


def create_window():
    if not glfw.init():
        raise RuntimeError("Unable to start GLFW.")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

    window = glfw.create_window(WIDTH, HEIGHT, TITLE, None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Unable to create the OpenGL window.")

    glfw.make_context_current(window)
    glfw.swap_interval(1)

    return window


def create_triangle():
    # x, y, r, g, b for each vertex, centred on the origin so it spins in place
    vertices = (ctypes.c_float * 15)(
         0.0,   0.6,  1.0, 0.0, 0.0,
        -0.52, -0.3,  0.0, 1.0, 0.0,
         0.52, -0.3,  0.0, 0.0, 1.0,
    )

    vertex_array = glGenVertexArrays(1)
    vertex_buffer = glGenBuffers(1)
    glBindVertexArray(vertex_array)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vertices), vertices, GL_STATIC_DRAW)

    stride = 5 * ctypes.sizeof(ctypes.c_float)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(2 * ctypes.sizeof(ctypes.c_float)))
    glEnableVertexAttribArray(1)

    return vertex_array, vertex_buffer


def draw(shader_program, vertex_array, width, height, elapsed, mode):
    transform = multiply_matrices(aspect_matrix(width, height), rotation_matrix(ROTATION_SPEED * elapsed))
    values = (ctypes.c_float * 16)(*[value for row in transform for value in row])

    glViewport(0, 0, width, height)
    glClearColor(0.08, 0.08, 0.12, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    glUseProgram(shader_program)
    # GL_TRUE transposes on upload, so the matrix can be written row by row like experiments 6 and 7
    glUniformMatrix4fv(glGetUniformLocation(shader_program, "transform"), 1, GL_TRUE, values)
    glUniform1f(glGetUniformLocation(shader_program, "time"), elapsed)
    glUniform1i(glGetUniformLocation(shader_program, "mode"), mode)

    glBindVertexArray(vertex_array)
    glDrawArrays(GL_TRIANGLES, 0, 3)


def print_info():
    print(f"OpenGL version : {glGetString(GL_VERSION).decode()}")
    print(f"GLSL version   : {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
    print(f"Renderer       : {glGetString(GL_RENDERER).decode()}")
    print("\nControls")
    print("  1-4    change the fragment shader colour mode")
    print("  Space  pause or resume the animation")
    print("  Esc    close the window\n")


def show_mode(window, mode):
    glfw.set_window_title(window, f"{TITLE} - {MODE_NAMES[mode]}")
    print(f"Colour mode {mode + 1}: {MODE_NAMES[mode]}")


def main():
    window = create_window()
    shader_program = create_shader_program()
    vertex_array, vertex_buffer = create_triangle()
    state = {"mode": 0, "paused": False}

    def on_key(window, key, scancode, action, mods):
        if action != glfw.PRESS:
            return

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_SPACE:
            state["paused"] = not state["paused"]
        elif glfw.KEY_1 <= key <= glfw.KEY_4:
            state["mode"] = key - glfw.KEY_1
            show_mode(window, state["mode"])

    glfw.set_key_callback(window, on_key)
    print_info()
    show_mode(window, state["mode"])

    elapsed = 0.0
    last_time = glfw.get_time()

    while not glfw.window_should_close(window):
        now = glfw.get_time()

        if not state["paused"]:
            elapsed += now - last_time

        last_time = now
        width, height = glfw.get_framebuffer_size(window)

        if width > 0 and height > 0:
            draw(shader_program, vertex_array, width, height, elapsed, state["mode"])

        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, [vertex_array])
    glDeleteBuffers(1, [vertex_buffer])
    glDeleteProgram(shader_program)
    glfw.terminate()


if __name__ == "__main__":
    main()
