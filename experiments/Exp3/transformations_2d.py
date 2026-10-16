"""Experiment 3: 2D transformations using homogeneous coordinates in OpenGL."""

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


WIDTH = 900
HEIGHT = 650
TITLE_HEIGHT = 80
FOOTER_HEIGHT = 40
LABEL_SPACE = 55


def identity_matrix():
    return [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]


def translation_matrix(tx, ty):
    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1],
    ]


def rotation_matrix(angle_in_degrees):
    angle = math.radians(angle_in_degrees)
    cos_value = math.cos(angle)
    sin_value = math.sin(angle)

    return [
        [cos_value, -sin_value, 0],
        [sin_value, cos_value, 0],
        [0, 0, 1],
    ]


def scaling_matrix(sx, sy):
    return [
        [sx, 0, 0],
        [0, sy, 0],
        [0, 0, 1],
    ]


def shearing_matrix(shx, shy):
    return [
        [1, shx, 0],
        [shy, 1, 0],
        [0, 0, 1],
    ]


def reflection_matrix(axis):
    if axis == "x":
        return scaling_matrix(1, -1)
    if axis == "y":
        return scaling_matrix(-1, 1)
    if axis == "origin":
        return scaling_matrix(-1, -1)
    if axis == "y=x":
        return [
            [0, 1, 0],
            [1, 0, 0],
            [0, 0, 1],
        ]

    return [
        [0, -1, 0],
        [-1, 0, 0],
        [0, 0, 1],
    ]


def multiply_matrices(a, b):
    result = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    for row in range(3):
        for column in range(3):
            total = 0

            for k in range(3):
                total += a[row][k] * b[k][column]

            result[row][column] = total

    return result


def about_point(matrix, px, py):
    shifted = multiply_matrices(translation_matrix(px, py), matrix)

    return multiply_matrices(shifted, translation_matrix(-px, -py))


def transform_points(matrix, points):
    transformed = []

    for x, y in points:
        new_x = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2]
        new_y = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2]
        w = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2]
        transformed.append((clean(new_x / w), clean(new_y / w)))

    return transformed


def clean(value):
    if abs(value) < 1e-9:
        return 0.0

    return round(value, 6)


def print_matrix(matrix):
    for row in matrix:
        print("  ".join(f"{clean(value):7.2f}" for value in row))


def to_opengl_matrix(matrix):
    # The 3x3 homogeneous matrix placed in a 4x4 OpenGL matrix (z is left unchanged),
    # written column by column because OpenGL stores matrices in column-major order
    (a, b, c), (d, e, f), (g, h, i) = matrix

    return [
        a, d, 0, g,
        b, e, 0, h,
        0, 0, 1, 0,
        c, f, 0, i,
    ]


def get_graph_bounds(points):
    x_values = [x for x, y in points]
    y_values = [y for x, y in points]

    min_x = math.floor(min(x_values))
    max_x = math.ceil(max(x_values))
    min_y = math.floor(min(y_values))
    max_y = math.ceil(max(y_values))

    x_padding = max(1, (max_x - min_x) // 5)
    y_padding = max(1, (max_y - min_y) // 5)

    return min_x - x_padding, max_x + x_padding, min_y - y_padding, max_y + y_padding


def choose_grid_step(min_value, max_value):
    graph_range = max_value - min_value

    if graph_range <= 20:
        return 1
    if graph_range <= 50:
        return 5
    if graph_range <= 100:
        return 10

    return 20


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_12):
    glRasterPos2f(x, y)

    for character in text:
        glutBitmapCharacter(font, ord(character))


def text_width(text, font=GLUT_BITMAP_HELVETICA_12):
    return sum(glutBitmapWidth(font, ord(character)) for character in text)


def pixel_view(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def graph_view(min_x, max_x, min_y, max_y, left, bottom, width, height):
    # Window-to-viewport mapping: the world window has the same aspect ratio as the viewport,
    # so one unit is the same number of pixels along both axes and shapes are not stretched
    scale = min((width - 2 * LABEL_SPACE) / (max_x - min_x), (height - 2 * LABEL_SPACE) / (max_y - min_y))
    centre_x = (min_x + max_x) / 2
    centre_y = (min_y + max_y) / 2
    half_width = width / (2 * scale)
    half_height = height / (2 * scale)

    glViewport(int(left), int(bottom), int(width), int(height))
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(centre_x - half_width, centre_x + half_width, centre_y - half_height, centre_y + half_height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    return 1 / scale


def draw_grid(min_x, max_x, min_y, max_y, unit):
    x_step = choose_grid_step(min_x, max_x)
    y_step = choose_grid_step(min_y, max_y)
    x_values = range(math.ceil(min_x / x_step) * x_step, max_x + 1, x_step)
    y_values = range(math.ceil(min_y / y_step) * y_step, max_y + 1, y_step)

    glColor3f(0.87, 0.87, 0.87)
    glBegin(GL_LINES)

    for x in x_values:
        glVertex2f(x, min_y)
        glVertex2f(x, max_y)

    for y in y_values:
        glVertex2f(min_x, y)
        glVertex2f(max_x, y)

    glEnd()

    glColor3f(0, 0, 0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(min_x, min_y)
    glVertex2f(max_x, min_y)
    glVertex2f(max_x, max_y)
    glVertex2f(min_x, max_y)
    glEnd()

    glLineWidth(2)
    glBegin(GL_LINES)

    if min_y <= 0 <= max_y:
        glVertex2f(min_x, 0)
        glVertex2f(max_x, 0)

    if min_x <= 0 <= max_x:
        glVertex2f(0, min_y)
        glVertex2f(0, max_y)

    glEnd()
    glLineWidth(1)

    glColor3f(0.35, 0.35, 0.35)

    for x in x_values:
        draw_text(x - text_width(str(x), GLUT_BITMAP_HELVETICA_10) * unit / 2, min_y - 16 * unit, str(x), GLUT_BITMAP_HELVETICA_10)

    for y in y_values:
        draw_text(min_x - (text_width(str(y), GLUT_BITMAP_HELVETICA_10) + 8) * unit, y - 3 * unit, str(y), GLUT_BITMAP_HELVETICA_10)

    glColor3f(0, 0, 0)
    draw_text(max_x + 8 * unit, min_y - 4 * unit, "X")
    draw_text(min_x - 4 * unit, max_y + 10 * unit, "Y")


def draw_shape(points, color, dashed, width):
    glColor3f(*color)
    glLineWidth(width)

    if dashed:
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(2, 0x00FF)

    glBegin(GL_LINE_LOOP if len(points) > 2 else GL_LINE_STRIP)

    for x, y in points:
        glVertex2f(x, y)

    glEnd()
    glDisable(GL_LINE_STIPPLE)
    glLineWidth(1)


def plot_points(points, color, unit):
    glColor3f(*color)
    glPointSize(8)
    glBegin(GL_POINTS)

    for x, y in points:
        glVertex2f(x, y)

    glEnd()

    for x, y in points:
        draw_text(x + 8 * unit, y + 6 * unit, f"({x:g}, {y:g})", GLUT_BITMAP_HELVETICA_10)


def draw_matrix(matrix, right, top):
    rows = [" ".join(f"{clean(value):7.2f}" for value in values) for values in matrix]
    left = right - max(text_width(row, GLUT_BITMAP_9_BY_15) for row in rows)

    glColor3f(0, 0, 0)
    draw_text(left, top, "Homogeneous matrix M:")

    for i, row in enumerate(rows):
        draw_text(left, top - 18 * (i + 1), row, GLUT_BITMAP_9_BY_15)


def read_shape():
    count = int(input("Number of vertices: "))

    if count < 2:
        raise SystemExit("A shape needs at least 2 vertices")

    points = []

    for i in range(count):
        x = float(input(f"x{i + 1}: "))
        y = float(input(f"y{i + 1}: "))
        points.append((x, y))

    return points


def read_transformation():
    print("\nChoose a transformation")
    print("1. Translation")
    print("2. Rotation")
    print("3. Scaling")
    print("4. Reflection")
    print("5. Shearing")
    choice = input("Choice: ").strip()

    if choice == "1":
        tx = float(input("tx: "))
        ty = float(input("ty: "))

        return translation_matrix(tx, ty), f"Translation by ({tx:g}, {ty:g})"

    if choice == "2":
        angle = float(input("Angle in degrees (anticlockwise): "))
        px = float(input("Pivot x: "))
        py = float(input("Pivot y: "))

        return about_point(rotation_matrix(angle), px, py), f"Rotation of {angle:g} degrees about ({px:g}, {py:g})"

    if choice == "3":
        sx = float(input("sx: "))
        sy = float(input("sy: "))
        px = float(input("Fixed point x: "))
        py = float(input("Fixed point y: "))

        return about_point(scaling_matrix(sx, sy), px, py), f"Scaling by ({sx:g}, {sy:g}) about ({px:g}, {py:g})"

    if choice == "4":
        return read_reflection()

    if choice == "5":
        shx = float(input("Shear along x (shx): "))
        shy = float(input("Shear along y (shy): "))

        return shearing_matrix(shx, shy), f"Shearing by ({shx:g}, {shy:g})"

    raise SystemExit("Invalid transformation choice")


def read_reflection():
    print("\nReflect about")
    print("1. X axis")
    print("2. Y axis")
    print("3. Origin")
    print("4. Line y = x")
    print("5. Line y = -x")
    choice = input("Choice: ").strip()

    axes = {"1": "x", "2": "y", "3": "origin", "4": "y=x", "5": "y=-x"}
    labels = {
        "x": "X axis",
        "y": "Y axis",
        "origin": "origin",
        "y=x": "line y = x",
        "y=-x": "line y = -x",
    }

    if choice not in axes:
        raise SystemExit("Invalid reflection choice")

    axis = axes[choice]

    return reflection_matrix(axis), f"Reflection about the {labels[axis]}"


def main():
    print("Enter the shape vertices")
    original = read_shape()

    matrix, name = read_transformation()
    transformed = transform_points(matrix, original)

    print(f"\n{name}")
    print("\nHomogeneous transformation matrix:")
    print_matrix(matrix)

    print("\nOriginal -> Transformed:")
    for (x, y), (new_x, new_y) in zip(original, transformed):
        print(f"({x:g}, {y:g}) -> ({new_x:g}, {new_y:g})")

    min_x, max_x, min_y, max_y = get_graph_bounds(original + transformed)

    def display():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)

        glClear(GL_COLOR_BUFFER_BIT)
        unit = graph_view(min_x, max_x, min_y, max_y, 0, FOOTER_HEIGHT, width, height - TITLE_HEIGHT - FOOTER_HEIGHT)
        draw_grid(min_x, max_x, min_y, max_y, unit)
        draw_shape(original, (0.1, 0.2, 0.9), True, 2)

        # OpenGL applies the same homogeneous matrix to the original vertices
        glPushMatrix()
        glMultMatrixf(to_opengl_matrix(matrix))
        draw_shape(original, (0.9, 0.1, 0.1), False, 2.5)
        glPopMatrix()

        plot_points(original, (0.1, 0.2, 0.9), unit)
        plot_points(transformed, (0.9, 0.1, 0.1), unit)

        pixel_view(width, height)
        glColor3f(0, 0, 0)
        draw_text(20, height - 30, name, GLUT_BITMAP_HELVETICA_18)
        glColor3f(0.1, 0.2, 0.9)
        draw_text(20, height - 55, "blue dashed = original")
        glColor3f(0.9, 0.1, 0.1)
        draw_text(170, height - 55, "red = drawn by OpenGL with glMultMatrixf(M)")
        glColor3f(0.3, 0.3, 0.3)
        draw_text(20, 14, "Dots = vertices computed by multiplying each point [x, y, 1] by M      Esc: close")
        draw_matrix(matrix, width - 20, height - 22)
        glutSwapBuffers()

    def keyboard(key, x, y):
        if key == b"\x1b":
            glutLeaveMainLoop()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"2D Transformations using Homogeneous Coordinates")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glClearColor(1, 1, 1, 1)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
