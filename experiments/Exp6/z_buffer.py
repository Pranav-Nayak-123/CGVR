"""Experiment 6: Z-buffer (depth buffer) algorithm for hidden surface removal using OpenGL."""

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


PANEL_SIZE = 300
PANEL_GAP = 25
MARGIN = 30
TITLE_HEIGHT = 95
FOOTER_HEIGHT = 110
WIDTH = 3 * PANEL_SIZE + 2 * PANEL_GAP + 2 * MARGIN
HEIGHT = TITLE_HEIGHT + PANEL_SIZE + FOOTER_HEIGHT
SCALE = 70
BACKGROUND = (20, 20, 30)
LIGHT_DIRECTION = (0.4, 0.8, 0.45)
ROTATION_STEP = 10

CUBE_COLOR = (70, 130, 230)
PYRAMID_COLOR = (240, 150, 40)
PLATE_COLOR = (60, 190, 110)


def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def normalize(vector):
    length = math.sqrt(dot(vector, vector))

    return (vector[0] / length, vector[1] / length, vector[2] / length)


def make_cube(center, half, color):
    cx, cy, cz = center
    x0, x1 = cx - half, cx + half
    y0, y1 = cy - half, cy + half
    z0, z1 = cz - half, cz + half

    # Front faces are listed before back faces, so drawing in list order without a
    # depth test lets the back faces paint over the front ones
    return [
        ("Cube front", [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], color),
        ("Cube top", [(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)], color),
        ("Cube right", [(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)], color),
        ("Cube back", [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)], color),
        ("Cube bottom", [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], color),
        ("Cube left", [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)], color),
    ]


def make_pyramid(base_center, half, height, color):
    bx, by, bz = base_center
    apex = (bx, by + height, bz)
    front_left = (bx - half, by, bz + half)
    front_right = (bx + half, by, bz + half)
    back_right = (bx + half, by, bz - half)
    back_left = (bx - half, by, bz - half)

    return [
        ("Pyramid front", [front_left, front_right, apex], color),
        ("Pyramid right", [front_right, back_right, apex], color),
        ("Pyramid back", [back_right, back_left, apex], color),
        ("Pyramid left", [back_left, front_left, apex], color),
        ("Pyramid base", [back_left, back_right, front_right, front_left], color),
    ]


def make_plate(color):
    # A tilted plate that passes through both solids, so parts of it are inside them
    return [
        ("Slanted plate", [(-1.7, -0.45, 1.0), (1.7, -0.45, 1.0), (1.7, 0.25, -1.0), (-1.7, 0.25, -1.0)], color),
    ]


def shade(points, color):
    # Flat shading only so that neighbouring faces of the same object look different
    normal = normalize(cross(subtract(points[1], points[0]), subtract(points[2], points[0])))
    brightness = 0.45 + 0.55 * abs(dot(normal, normalize(LIGHT_DIRECTION)))

    return tuple(int(channel * brightness) for channel in color)


def build_scene():
    faces = []
    shapes = (
        make_cube((-0.7, 0.0, 0.0), 0.75, CUBE_COLOR)
        + make_pyramid((0.95, -0.75, 0.0), 0.65, 1.5, PYRAMID_COLOR)
        + make_plate(PLATE_COLOR)
    )

    for name, points, color in shapes:
        faces.append({"name": name, "points": points, "color": shade(points, color)})

    return faces


def rotate_view(point, yaw, pitch):
    x, y, z = point
    yaw = math.radians(yaw)
    pitch = math.radians(pitch)

    # Rotation about the Y axis, then about the X axis
    x, z = x * math.cos(yaw) + z * math.sin(yaw), -x * math.sin(yaw) + z * math.cos(yaw)
    y, z = y * math.cos(pitch) - z * math.sin(pitch), y * math.sin(pitch) + z * math.cos(pitch)

    return x, y, z


def to_screen(point):
    x, y, z = point

    # Orthographic projection. The viewer looks along -z, so depth = -z and a
    # smaller depth means the surface is closer to the viewer
    return PANEL_SIZE / 2 + SCALE * x, PANEL_SIZE / 2 - SCALE * y, -z


def screen_faces(faces, yaw, pitch):
    return [[to_screen(rotate_view(point, yaw, pitch)) for point in face["points"]] for face in faces]


def plane_coefficients(points):
    # Plane Ax + By + Cz + D = 0 through the first three vertices of the face
    (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = points[:3]
    a = (y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1)
    b = (z2 - z1) * (x3 - x1) - (x2 - x1) * (z3 - z1)
    c = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    d = -(a * x1 + b * y1 + c * z1)

    return a, b, c, d


def edge_crossings(points, y):
    crossings = []

    for i in range(len(points)):
        x1, y1, z1 = points[i]
        x2, y2, z2 = points[(i + 1) % len(points)]

        if y1 <= y < y2 or y2 <= y < y1:
            crossings.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))

    return crossings


def scan_convert_face(points, color, face_index, frame, depth, owner):
    a, b, c, d = plane_coefficients(points)

    if abs(c) < 1e-9:
        # The face is seen edge-on, so it covers no pixels
        return 0, 0

    tested = 0
    written = 0
    y_values = [y for x, y, z in points]
    first_row = max(0, math.ceil(min(y_values) - 0.5))
    last_row = min(PANEL_SIZE - 1, math.ceil(max(y_values) - 0.5) - 1)

    for row in range(first_row, last_row + 1):
        y = row + 0.5
        crossings = edge_crossings(points, y)

        if len(crossings) < 2:
            continue

        first_column = max(0, math.ceil(min(crossings) - 0.5))
        last_column = min(PANEL_SIZE - 1, math.ceil(max(crossings) - 0.5) - 1)

        if first_column > last_column:
            continue

        # Depth at the first pixel comes from the plane equation, then each step to the
        # right along the scan line only needs one addition: z(x + 1) = z(x) - A / C
        z = -(a * (first_column + 0.5) + b * y + d) / c
        step = -a / c

        for column in range(first_column, last_column + 1):
            tested += 1

            # The depth test: keep the new surface only if it is nearer than the stored one
            if z < depth[row][column]:
                depth[row][column] = z
                frame[row][column] = color
                owner[row][column] = face_index
                written += 1

            z += step

    return tested, written


def z_buffer_render(faces, projected):
    # Frame buffer starts with the background colour and the depth buffer with the
    # farthest possible depth (infinity)
    frame = [[BACKGROUND] * PANEL_SIZE for _ in range(PANEL_SIZE)]
    depth = [[math.inf] * PANEL_SIZE for _ in range(PANEL_SIZE)]
    owner = [[None] * PANEL_SIZE for _ in range(PANEL_SIZE)]
    counts = []

    for index, (face, points) in enumerate(zip(faces, projected)):
        counts.append(scan_convert_face(points, face["color"], index, frame, depth, owner))

    return frame, depth, owner, counts


def count_visible(faces, owner):
    visible = [0] * len(faces)

    for row in owner:
        for face_index in row:
            if face_index is not None:
                visible[face_index] += 1

    return visible


def face_status(tested, visible):
    if tested == 0:
        return "edge-on"
    if visible == 0:
        return "hidden"
    if visible == tested:
        return "fully visible"

    return "partly hidden"


def print_report(faces, depth, owner, counts, yaw, pitch):
    visible = count_visible(faces, owner)
    total_tested = sum(tested for tested, written in counts)
    total_written = sum(written for tested, written in counts)

    print(f"\nView: {yaw:g} degrees about the Y axis, then {pitch:g} degrees about the X axis")
    print(f"Frame buffer and depth buffer size: {PANEL_SIZE} x {PANEL_SIZE}")
    print("Depth buffer initialised to infinity, frame buffer to the background colour\n")
    print(f"{'Face':<16}{'Tested':>9}{'Written':>9}{'Visible':>9}   Result")

    for face, (tested, written), shown in zip(faces, counts, visible):
        print(f"{face['name']:<16}{tested:>9}{written:>9}{shown:>9}   {face_status(tested, shown)}")

    print(f"\nDepth comparisons made        : {total_tested}")
    print(f"Pixels written to the buffers : {total_written}")
    print(f"Pixels rejected (hidden)      : {total_tested - total_written}")
    print(f"Pixels in the final image     : {sum(visible)}")

    centre = PANEL_SIZE // 2
    face_index = owner[centre][centre]

    if face_index is not None:
        print(f"\nPixel ({centre}, {centre}): depth = {depth[centre][centre]:.4f}, colour from {faces[face_index]['name']}")


def frame_to_bytes(frame):
    # glDrawPixels fills the image from the bottom row up, while row 0 of the buffer is the top
    data = bytearray()

    for row in reversed(frame):
        for red, green, blue in row:
            data += bytes((red, green, blue))

    return bytes(data)


def depth_to_bytes(depth):
    values = [z for row in depth for z in row if z != math.inf]
    nearest = min(values)
    span = (max(values) - nearest) or 1
    data = bytearray()

    for row in reversed(depth):
        for z in row:
            # Nearest surface is brightest, farthest visible surface is dark grey, empty is black
            level = 0 if z == math.inf else int(235 - 175 * (z - nearest) / span)
            data += bytes((level, level, level))

    return bytes(data)


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


def draw_faces_with_opengl(faces, projected, left, bottom, use_depth_test):
    # Same screen coordinates as the software Z-buffer: x right, y down, and z = -depth so that
    # glOrtho maps a smaller depth to a smaller window depth (nearer, as GL_LESS expects)
    glViewport(left, bottom, PANEL_SIZE, PANEL_SIZE)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, PANEL_SIZE, PANEL_SIZE, 0, -10, 10)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glScissor(left, bottom, PANEL_SIZE, PANEL_SIZE)
    glEnable(GL_SCISSOR_TEST)
    glClearColor(*(channel / 255 for channel in BACKGROUND), 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_SCISSOR_TEST)
    glClearColor(1, 1, 1, 1)

    if use_depth_test:
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

    for face, points in zip(faces, projected):
        glColor3ub(*face["color"])
        glBegin(GL_POLYGON)

        for x, y, depth in points:
            glVertex3f(x, y, -depth)

        glEnd()

    glDisable(GL_DEPTH_TEST)


def draw_legend(y):
    items = [("Cube", CUBE_COLOR), ("Pyramid", PYRAMID_COLOR), ("Slanted plate", PLATE_COLOR)]
    x = MARGIN

    for name, color in items:
        glColor3ub(*color)
        glRectf(x, y - 6, x + 12, y + 6)
        glColor3f(0, 0, 0)
        draw_text(x + 18, y - 4, name)
        x += 120


def read_number(prompt, default):
    text = input(f"{prompt} [{default:g}]: ").strip()

    return float(text) if text else default


def main():
    print("Z-Buffer Algorithm for Hidden Surface Removal")
    print("Press Enter to accept the default value shown in brackets\n")
    state = {
        "yaw": read_number("Rotation about the Y axis in degrees", -20),
        "pitch": read_number("Rotation about the X axis in degrees", 20),
        "hardware": False,
    }
    faces = build_scene()

    def update_buffers():
        projected = screen_faces(faces, state["yaw"], state["pitch"])
        frame, depth, owner, counts = z_buffer_render(faces, projected)
        state.update(projected=projected, depth=depth, owner=owner, counts=counts)
        state["frame_bytes"] = frame_to_bytes(frame)
        state["depth_bytes"] = depth_to_bytes(depth)

    update_buffers()
    print_report(faces, state["depth"], state["owner"], state["counts"], state["yaw"], state["pitch"])

    def display():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)
        bottom = FOOTER_HEIGHT
        lefts = [MARGIN + i * (PANEL_SIZE + PANEL_GAP) for i in range(3)]
        total_tested = sum(tested for tested, written in state["counts"])
        total_written = sum(written for tested, written in state["counts"])

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Panel 1: OpenGL draws the faces in list order with no depth test
        draw_faces_with_opengl(faces, state["projected"], lefts[0], bottom, False)

        # Panel 2: our Z-buffer result copied to the screen, or OpenGL's own depth test for comparison
        if state["hardware"]:
            draw_faces_with_opengl(faces, state["projected"], lefts[1], bottom, True)
        else:
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glWindowPos2i(lefts[1], bottom)
            glDrawPixels(PANEL_SIZE, PANEL_SIZE, GL_RGB, GL_UNSIGNED_BYTE, state["frame_bytes"])

        # Panel 3: the contents of our depth buffer as grey levels
        glWindowPos2i(lefts[2], bottom)
        glDrawPixels(PANEL_SIZE, PANEL_SIZE, GL_RGB, GL_UNSIGNED_BYTE, state["depth_bytes"])

        pixel_view(width, height)
        titles = [
            "Without depth test (list order)",
            "OpenGL GL_DEPTH_TEST" if state["hardware"] else "With Z-buffer (our algorithm)",
            "Depth buffer (brighter = nearer)",
        ]

        for left, title in zip(lefts, titles):
            glColor3f(0, 0, 0)
            draw_text(left + (PANEL_SIZE - text_width(title)) / 2, bottom + PANEL_SIZE + 12, title)
            glBegin(GL_LINE_LOOP)
            glVertex2f(left, bottom)
            glVertex2f(left + PANEL_SIZE, bottom)
            glVertex2f(left + PANEL_SIZE, bottom + PANEL_SIZE)
            glVertex2f(left, bottom + PANEL_SIZE)
            glEnd()

        glColor3f(0, 0, 0)
        draw_text(MARGIN, height - 30, "Z-Buffer Algorithm for Hidden Surface Removal", GLUT_BITMAP_HELVETICA_18)
        glColor3f(0.35, 0.35, 0.35)
        draw_text(
            MARGIN,
            height - 54,
            "For every pixel of every face: if z < depth(x, y) then depth(x, y) = z and frame(x, y) = face colour"
            f"      View: {state['yaw']:g} deg about Y, {state['pitch']:g} deg about X",
        )

        draw_legend(bottom - 25)
        glColor3f(0, 0, 0)
        draw_text(
            MARGIN,
            bottom - 55,
            f"Depth comparisons: {total_tested}      Pixels written: {total_written}"
            f"      Rejected by the depth test: {total_tested - total_written}",
        )
        glColor3f(0.35, 0.35, 0.35)
        draw_text(MARGIN, bottom - 85, "Arrow keys: rotate the view      H: switch panel 2 between our Z-buffer and OpenGL's      Esc: close")
        glutSwapBuffers()

    def keyboard(key, x, y):
        if key == b"\x1b":
            glutLeaveMainLoop()
        elif key in (b"h", b"H"):
            state["hardware"] = not state["hardware"]
            glutPostRedisplay()

    def special_keys(key, x, y):
        changes = {
            GLUT_KEY_LEFT: (-ROTATION_STEP, 0),
            GLUT_KEY_RIGHT: (ROTATION_STEP, 0),
            GLUT_KEY_UP: (0, ROTATION_STEP),
            GLUT_KEY_DOWN: (0, -ROTATION_STEP),
        }

        if key in changes:
            state["yaw"] += changes[key][0]
            state["pitch"] += changes[key][1]
            update_buffers()
            glutPostRedisplay()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Z-Buffer Hidden Surface Removal")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glClearColor(1, 1, 1, 1)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMainLoop()


if __name__ == "__main__":
    main()
