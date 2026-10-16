"""Experiment 2: Midpoint circle drawing algorithm using OpenGL."""

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


WIDTH = 900
HEIGHT = 650
TITLE_HEIGHT = 60
FOOTER_HEIGHT = 70
LABEL_SPACE = 45

# Each computed point (x, y) of the first octant gives one pixel in all eight octants
OCTANTS = [
    ("(x, y)", 1, 1, False, (0.90, 0.20, 0.20)),
    ("(y, x)", 1, 1, True, (0.95, 0.55, 0.10)),
    ("(-x, y)", -1, 1, False, (0.80, 0.70, 0.05)),
    ("(-y, x)", -1, 1, True, (0.25, 0.70, 0.30)),
    ("(-x, -y)", -1, -1, False, (0.10, 0.70, 0.75)),
    ("(-y, -x)", -1, -1, True, (0.20, 0.35, 0.90)),
    ("(x, -y)", 1, -1, False, (0.55, 0.30, 0.85)),
    ("(y, -x)", 1, -1, True, (0.85, 0.30, 0.60)),
]


def midpoint_circle(r):
    # Points of the second octant (from (0, r) until x >= y), relative to the centre
    x = 0
    y = r
    decision = 1 - r
    points = [(x, y)]
    rows = []

    while x < y:
        used = decision
        x += 1

        if decision < 0:
            decision += 2 * x + 1
        else:
            y -= 1
            decision += 2 * (x - y) + 1

        rows.append((used, x, y))
        points.append((x, y))

    return points, rows


def symmetric_pixels(points, xc, yc):
    pixels = {}

    for x, y in points:
        for index, (name, sign_x, sign_y, swap, color) in enumerate(OCTANTS):
            px, py = (y, x) if swap else (x, y)
            pixels[(xc + sign_x * px, yc + sign_y * py)] = index

    return pixels


def get_graph_bounds(points):
    x_values = [x for x, y in points]
    y_values = [y for x, y in points]

    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)

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
    # so one unit is the same number of pixels along both axes and the circle stays round
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

    if max(max_x - min_x, max_y - min_y) <= 100:
        # Faint line at every pixel boundary, darker lines where the axis is labelled
        glColor3f(0.94, 0.94, 0.94)
        glBegin(GL_LINES)

        for x in range(min_x, max_x + 1):
            glVertex2f(x, min_y)
            glVertex2f(x, max_y)

        for y in range(min_y, max_y + 1):
            glVertex2f(min_x, y)
            glVertex2f(max_x, y)

        glEnd()

    glColor3f(0.8, 0.8, 0.8)
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


def draw_pixels(pixels):
    # Each raster pixel is a unit square centred on its integer coordinates, coloured by octant
    for (x, y), index in pixels.items():
        red, green, blue = OCTANTS[index][4]
        glColor3f(red, green, blue)
        glRectf(x - 0.5, y - 0.5, x + 0.5, y + 0.5)
        glColor3f(red * 0.5, green * 0.5, blue * 0.5)
        glBegin(GL_LINE_LOOP)
        glVertex2f(x - 0.5, y - 0.5)
        glVertex2f(x + 0.5, y - 0.5)
        glVertex2f(x + 0.5, y + 0.5)
        glVertex2f(x - 0.5, y + 0.5)
        glEnd()


def draw_ideal_circle(xc, yc, r):
    glColor3f(0, 0, 0)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)

    for i in range(120):
        angle = 2 * math.pi * i / 120
        glVertex2f(xc + r * math.cos(angle), yc + r * math.sin(angle))

    glEnd()
    glLineWidth(1)

    glPointSize(6)
    glBegin(GL_POINTS)
    glVertex2f(xc, yc)
    glEnd()


def draw_legend(width):
    x = 20
    glColor3f(0.2, 0.2, 0.2)
    draw_text(x, 42, "Octant of each pixel (from the computed point x, y):")

    for name, sign_x, sign_y, swap, color in OCTANTS:
        glColor3f(*color)
        glRectf(x, 14, x + 14, 28)
        glColor3f(0, 0, 0)
        draw_text(x + 20, 16, name)
        x += 22 + text_width(name) + 28


def print_table(xc, yc, r, rows, pixel_count):
    print(f"\nInitial decision parameter p0 = 1 - r = {1 - r}")
    print("Points of one octant, relative to the centre (each is mirrored into all 8 octants)\n")
    print(f"{'k':>3}  {'p_k':>6}  {'(x, y)':>10}  {'pixel in this octant':>22}")
    print(f"{'-':>3}  {'-':>6}  {f'(0, {r})':>10}  {f'({xc}, {yc + r})':>22}")

    for k, (used, x, y) in enumerate(rows):
        print(f"{k:>3}  {used:>6}  {f'({x}, {y})':>10}  {f'({xc + x}, {yc + y})':>22}")

    print(f"\nPoints computed: {len(rows) + 1}, pixels plotted using 8-way symmetry: {pixel_count}")


def main():
    print("Midpoint Circle Drawing Algorithm")
    xc = int(input("xc: "))
    yc = int(input("yc: "))
    r = int(input("r: "))

    if r < 0:
        raise SystemExit("Radius cannot be negative")

    points, rows = midpoint_circle(r)
    pixels = symmetric_pixels(points, xc, yc)
    print_table(xc, yc, r, rows, len(pixels))
    min_x, max_x, min_y, max_y = get_graph_bounds(list(pixels))

    def display():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)

        glClear(GL_COLOR_BUFFER_BIT)
        unit = graph_view(min_x, max_x, min_y, max_y, 0, FOOTER_HEIGHT, width, height - TITLE_HEIGHT - FOOTER_HEIGHT)
        draw_grid(min_x, max_x, min_y, max_y, unit)
        draw_pixels(pixels)
        draw_ideal_circle(xc, yc, r)

        pixel_view(width, height)
        glColor3f(0, 0, 0)
        draw_text(20, height - 32, f"Midpoint circle: centre ({xc}, {yc}), radius {r}", GLUT_BITMAP_HELVETICA_18)
        glColor3f(0.3, 0.3, 0.3)
        draw_text(width - 230, height - 32, f"{len(pixels)} pixels      Esc: close")
        draw_legend(width)
        glutSwapBuffers()

    def keyboard(key, x, y):
        if key == b"\x1b":
            glutLeaveMainLoop()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Midpoint Circle Drawing Algorithm")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glClearColor(1, 1, 1, 1)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
