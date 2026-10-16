"""Experiment 5: Cohen-Sutherland line clipping algorithm using OpenGL."""

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8
WIDTH = 900
HEIGHT = 650
TITLE_HEIGHT = 70
FOOTER_HEIGHT = 40
LABEL_SPACE = 55


def compute_outcode(x_value, y_value, xmin, ymin, xmax, ymax):
    code = INSIDE

    if x_value < xmin:
        code |= LEFT
    elif x_value > xmax:
        code |= RIGHT

    if y_value < ymin:
        code |= BOTTOM
    elif y_value > ymax:
        code |= TOP

    return code


def code_text(code):
    # Region code written as the four bits TOP BOTTOM RIGHT LEFT
    return format(code, "04b")


def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax, trace):
    code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    while True:
        trace.append(f"P1 = ({x1:.2f}, {y1:.2f}) code {code_text(code1)},  P2 = ({x2:.2f}, {y2:.2f}) code {code_text(code2)}")

        if code1 == 0 and code2 == 0:
            trace.append("Both codes are 0000: trivially accepted")
            return (x1, y1, x2, y2)

        if code1 & code2:
            trace.append(f"code1 AND code2 = {code_text(code1 & code2)} (not 0000): trivially rejected")
            return None

        outside_code = code1 if code1 != 0 else code2

        if outside_code & TOP:
            x_new = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y_new = ymax
            edge = "top edge y = ymax"
        elif outside_code & BOTTOM:
            x_new = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y_new = ymin
            edge = "bottom edge y = ymin"
        elif outside_code & RIGHT:
            y_new = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x_new = xmax
            edge = "right edge x = xmax"
        else:
            y_new = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x_new = xmin
            edge = "left edge x = xmin"

        point = "P1" if outside_code == code1 else "P2"
        trace.append(f"{point} is outside: intersect with the {edge} at ({x_new:.2f}, {y_new:.2f})")

        if outside_code == code1:
            x1, y1 = x_new, y_new
            code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x_new, y_new
            code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)


def read_point(label):
    x_value, y_value = map(float, input(f"Enter {label} (x y): ").split())
    return x_value, y_value


def get_graph_bounds(x_values, y_values):
    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)
    span_x = max(max_x - min_x, 1)
    span_y = max(max_y - min_y, 1)

    return (
        math.floor(min_x - span_x * 0.2),
        math.ceil(max_x + span_x * 0.2),
        math.floor(min_y - span_y * 0.2),
        math.ceil(max_y + span_y * 0.2),
    )


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

    return 1 / scale


def draw_grid(min_x, max_x, min_y, max_y, unit):
    x_step = choose_grid_step(min_x, max_x)
    y_step = choose_grid_step(min_y, max_y)
    x_values = range(math.ceil(min_x / x_step) * x_step, max_x + 1, x_step)
    y_values = range(math.ceil(min_y / y_step) * y_step, max_y + 1, y_step)

    glColor3f(0.9, 0.9, 0.9)
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

    glColor3f(0.35, 0.35, 0.35)

    for x in x_values:
        draw_text(x - text_width(str(x), GLUT_BITMAP_HELVETICA_10) * unit / 2, min_y - 16 * unit, str(x), GLUT_BITMAP_HELVETICA_10)

    for y in y_values:
        draw_text(min_x - (text_width(str(y), GLUT_BITMAP_HELVETICA_10) + 8) * unit, y - 3 * unit, str(y), GLUT_BITMAP_HELVETICA_10)


def draw_regions(xmin, ymin, xmax, ymax, bounds, unit):
    min_x, max_x, min_y, max_y = bounds

    # The window edges extended across the plane divide it into nine regions
    glColor3f(0.6, 0.6, 0.6)
    glEnable(GL_LINE_STIPPLE)
    glLineStipple(1, 0x0F0F)
    glBegin(GL_LINES)

    for x in (xmin, xmax):
        glVertex2f(x, min_y)
        glVertex2f(x, max_y)

    for y in (ymin, ymax):
        glVertex2f(min_x, y)
        glVertex2f(max_x, y)

    glEnd()
    glDisable(GL_LINE_STIPPLE)

    columns = [((min_x + xmin) / 2, LEFT), ((xmin + xmax) / 2, INSIDE), ((xmax + max_x) / 2, RIGHT)]
    rows = [((ymax + max_y) / 2, TOP), ((ymin + ymax) / 2, INSIDE), ((min_y + ymin) / 2, BOTTOM)]
    glColor3f(0.55, 0.55, 0.55)

    for x, x_bit in columns:
        for y, y_bit in rows:
            text = code_text(x_bit | y_bit)
            draw_text(x - text_width(text, GLUT_BITMAP_HELVETICA_18) * unit / 2, y, text, GLUT_BITMAP_HELVETICA_18)

    glColor3f(0, 0, 0)
    glLineWidth(3)
    glBegin(GL_LINE_LOOP)
    glVertex2f(xmin, ymin)
    glVertex2f(xmax, ymin)
    glVertex2f(xmax, ymax)
    glVertex2f(xmin, ymax)
    glEnd()
    glLineWidth(1)


def draw_lines(x1, y1, x2, y2, clipped_line, unit):
    glColor3f(0.9, 0.1, 0.1)
    glLineWidth(2)
    glEnable(GL_LINE_STIPPLE)
    glLineStipple(2, 0x00FF)
    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    glDisable(GL_LINE_STIPPLE)

    glPointSize(8)
    glBegin(GL_POINTS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()
    draw_text(x1 + 8 * unit, y1 - 16 * unit, f"P1 ({x1:g}, {y1:g})")
    draw_text(x2 + 8 * unit, y2 - 16 * unit, f"P2 ({x2:g}, {y2:g})")

    if clipped_line:
        clip_x1, clip_y1, clip_x2, clip_y2 = clipped_line
        glColor3f(0.1, 0.25, 0.9)
        glLineWidth(4)
        glBegin(GL_LINES)
        glVertex2f(clip_x1, clip_y1)
        glVertex2f(clip_x2, clip_y2)
        glEnd()
        glBegin(GL_POINTS)
        glVertex2f(clip_x1, clip_y1)
        glVertex2f(clip_x2, clip_y2)
        glEnd()
        draw_text(clip_x1 + 8 * unit, clip_y1 + 8 * unit, f"({clip_x1:.2f}, {clip_y1:.2f})")
        draw_text(clip_x2 + 8 * unit, clip_y2 + 8 * unit, f"({clip_x2:.2f}, {clip_y2:.2f})")

    glLineWidth(1)


def main():
    print("Cohen-Sutherland Line Clipping")
    print("Enter the clipping window and line endpoints as: x y")
    xmin, ymin = read_point("bottom-left corner")
    xmax, ymax = read_point("top-right corner")
    x1, y1 = read_point("first endpoint")
    x2, y2 = read_point("second endpoint")

    if xmin >= xmax or ymin >= ymax:
        print("Invalid clipping window. Minimum values must be smaller than maximum values.")
        return

    print("\nRegion code bits: TOP BOTTOM RIGHT LEFT\n")
    trace = []
    clipped_line = cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax, trace)

    for step in trace:
        print(step)

    if clipped_line:
        print("\nAccepted clipped line:")
        print(f"({clipped_line[0]:.2f}, {clipped_line[1]:.2f}) to ({clipped_line[2]:.2f}, {clipped_line[3]:.2f})")
        message = "Red dashed: original line      Blue: clipped line inside the window"
    else:
        print("\nRejected: the line lies completely outside the clipping window.")
        message = "Red dashed: original line      The line is completely outside the window"

    bounds = get_graph_bounds([x1, x2, xmin, xmax], [y1, y2, ymin, ymax])

    def display():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)

        glClear(GL_COLOR_BUFFER_BIT)
        unit = graph_view(*bounds, 0, FOOTER_HEIGHT, width, height - TITLE_HEIGHT - FOOTER_HEIGHT)
        draw_grid(*bounds, unit)
        draw_regions(xmin, ymin, xmax, ymax, bounds, unit)
        draw_lines(x1, y1, x2, y2, clipped_line, unit)

        pixel_view(width, height)
        glColor3f(0, 0, 0)
        draw_text(
            20,
            height - 30,
            f"Clipping window ({xmin:g}, {ymin:g}) to ({xmax:g}, {ymax:g})",
            GLUT_BITMAP_HELVETICA_18,
        )
        glColor3f(0.3, 0.3, 0.3)
        draw_text(20, height - 52, message)
        draw_text(20, 14, "Grey numbers = region codes (TOP BOTTOM RIGHT LEFT)      Esc: close")
        glutSwapBuffers()

    def keyboard(key, x, y):
        if key == b"\x1b":
            glutLeaveMainLoop()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Cohen-Sutherland Line Clipping")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glClearColor(1, 1, 1, 1)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
