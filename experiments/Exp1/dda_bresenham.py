"""Experiment 1: DDA and Bresenham line drawing algorithms using OpenGL."""

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


WIDTH = 1100
HEIGHT = 580
TITLE_HEIGHT = 70
FOOTER_HEIGHT = 45
PANEL_GAP = 20
LABEL_SPACE = 45
DDA_COLOR = (0.25, 0.45, 0.95)
BRESENHAM_COLOR = (0.9, 0.35, 0.25)


def dda_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        return [(x1, y1, x1, y1)], 0, 0

    x_increment = dx / steps
    y_increment = dy / steps
    x = x1
    y = y1
    rows = []

    for i in range(steps + 1):
        # Round half up (Python's round() would round 2.5 down to 2)
        rows.append((x, y, math.floor(x + 0.5), math.floor(y + 0.5)))
        x += x_increment
        y += y_increment

    return rows, x_increment, y_increment


def bresenham_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    decision = dx - dy
    integer_operations = 0
    rows = []

    while True:
        rows.append((x1, y1, decision))

        if x1 == x2 and y1 == y2:
            break

        double_decision = 2 * decision

        if double_decision > -dy:
            decision -= dy
            x1 += sx
            integer_operations += 2

        if double_decision < dx:
            decision += dx
            y1 += sy
            integer_operations += 2

    return rows, integer_operations


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
    # so one unit is the same number of pixels along both axes
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

    # World units per pixel, and the window y coordinate of the top edge of the graph
    return 1 / scale, bottom + height / 2 + (max_y - centre_y) * scale


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


def draw_pixels(pixels, color, unit):
    # Each raster pixel is drawn as a unit square centred on its integer coordinates
    glColor3f(*color)

    for x, y in pixels:
        glRectf(x - 0.5, y - 0.5, x + 0.5, y + 0.5)

    glColor3f(color[0] * 0.5, color[1] * 0.5, color[2] * 0.5)

    for x, y in pixels:
        glBegin(GL_LINE_LOOP)
        glVertex2f(x - 0.5, y - 0.5)
        glVertex2f(x + 0.5, y - 0.5)
        glVertex2f(x + 0.5, y + 0.5)
        glVertex2f(x - 0.5, y + 0.5)
        glEnd()

    glColor3f(0, 0, 0)

    for x, y in (pixels[0], pixels[-1]):
        draw_text(x + 0.5 + 4 * unit, y - 0.5 - 12 * unit, f"({x}, {y})", GLUT_BITMAP_HELVETICA_10)


def draw_ideal_line(x1, y1, x2, y2):
    glColor3f(0, 0, 0)
    glLineWidth(1.5)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    glLineWidth(1)


def print_tables(dda_rows, x_increment, y_increment, bresenham_rows):
    print(f"\nDDA: steps = {len(dda_rows) - 1}, x increment = {x_increment:g}, y increment = {y_increment:g}")
    print(f"{'k':>3}  {'x':>9}  {'y':>9}  {'pixel':>12}")

    for k, (x, y, px, py) in enumerate(dda_rows):
        print(f"{k:>3}  {x:>9.3f}  {y:>9.3f}  {f'({px}, {py})':>12}")

    print("\nBresenham: e starts at dx - dy and only integer additions are used")
    print(f"{'k':>3}  {'pixel':>12}  {'e':>6}")

    for k, (x, y, decision) in enumerate(bresenham_rows):
        print(f"{k:>3}  {f'({x}, {y})':>12}  {decision:>6}")


def print_comparison(dda_pixels, bresenham_pixels, integer_operations):
    steps = len(dda_pixels) - 1
    only_dda = sorted(set(dda_pixels) - set(bresenham_pixels))
    only_bresenham = sorted(set(bresenham_pixels) - set(dda_pixels))

    print("\nComparison")
    print(f"Pixels plotted            : DDA {len(dda_pixels)}, Bresenham {len(bresenham_pixels)}")
    print(f"DDA floating-point work   : 2 divisions + {2 * steps} additions + {2 * (steps + 1)} roundings")
    print(f"Bresenham integer work    : {integer_operations} integer additions, no floating point")

    if only_dda or only_bresenham:
        print("Only chosen by DDA        : " + ", ".join(f"({x}, {y})" for x, y in only_dda))
        print("Only chosen by Bresenham  : " + ", ".join(f"({x}, {y})" for x, y in only_bresenham))
        print("(These are points where the ideal line passes exactly half way between two pixels)")
    else:
        print("Both algorithms selected exactly the same pixels")


def main():
    print("DDA and Bresenham Line Drawing Algorithms")
    x1 = int(input("x1: "))
    y1 = int(input("y1: "))
    x2 = int(input("x2: "))
    y2 = int(input("y2: "))

    dda_rows, x_increment, y_increment = dda_line(x1, y1, x2, y2)
    bresenham_rows, integer_operations = bresenham_line(x1, y1, x2, y2)
    dda_pixels = [(px, py) for x, y, px, py in dda_rows]
    bresenham_pixels = [(x, y) for x, y, decision in bresenham_rows]

    print_tables(dda_rows, x_increment, y_increment, bresenham_rows)
    print_comparison(dda_pixels, bresenham_pixels, integer_operations)

    min_x, max_x, min_y, max_y = get_graph_bounds(dda_pixels + bresenham_pixels)
    panels = [
        ("DDA: floating-point increments, rounded", dda_pixels, DDA_COLOR),
        ("Bresenham: integer decision parameter only", bresenham_pixels, BRESENHAM_COLOR),
    ]

    def display():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)
        panel_width = (width - 3 * PANEL_GAP) / 2
        panel_height = height - TITLE_HEIGHT - FOOTER_HEIGHT

        glClear(GL_COLOR_BUFFER_BIT)
        graph_top = 0

        for i, (name, pixels, color) in enumerate(panels):
            left = PANEL_GAP + i * (panel_width + PANEL_GAP)
            unit, graph_top = graph_view(min_x, max_x, min_y, max_y, left, FOOTER_HEIGHT, panel_width, panel_height)
            draw_grid(min_x, max_x, min_y, max_y, unit)
            draw_pixels(pixels, color, unit)
            draw_ideal_line(x1, y1, x2, y2)

        pixel_view(width, height)
        glColor3f(0, 0, 0)
        draw_text(PANEL_GAP, height - 30, f"Line from ({x1}, {y1}) to ({x2}, {y2})", GLUT_BITMAP_HELVETICA_18)

        for i, (name, pixels, color) in enumerate(panels):
            left = PANEL_GAP + i * (panel_width + PANEL_GAP)
            glColor3f(*color)
            draw_text(left + (panel_width - text_width(name, GLUT_BITMAP_HELVETICA_18)) / 2, graph_top + 30, name, GLUT_BITMAP_HELVETICA_18)

        glColor3f(0.3, 0.3, 0.3)
        draw_text(
            PANEL_GAP,
            15,
            f"Black line = ideal line      DDA pixels: {len(dda_pixels)}      Bresenham pixels: {len(bresenham_pixels)}"
            "      Esc: close",
        )
        glutSwapBuffers()

    def keyboard(key, x, y):
        if key == b"\x1b":
            glutLeaveMainLoop()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"DDA and Bresenham Line Drawing")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glClearColor(1, 1, 1, 1)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
