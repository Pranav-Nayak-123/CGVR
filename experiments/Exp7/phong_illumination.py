"""Experiment 7: Phong illumination model for a 3D object (sphere) using OpenGL."""

import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


PANEL_SIZE = 230
PANEL_GAP = 20
MARGIN = 30
TITLE_HEIGHT = 95
FOOTER_HEIGHT = 90
WIDTH = 4 * PANEL_SIZE + 3 * PANEL_GAP + 2 * MARGIN
HEIGHT = TITLE_HEIGHT + PANEL_SIZE + FOOTER_HEIGHT
BACKGROUND = (0.08, 0.08, 0.12)

SPHERE_RADIUS = 1.0
SLICES = 96
STACKS = 72
VIEWER = (0.0, 0.0, 6.0)
OBJECT_COLOR = (0.2, 0.45, 0.95)
SPECULAR_COLOR = (1.0, 1.0, 1.0)
AMBIENT_INTENSITY = 1.0
LIGHT_INTENSITY = 1.0
LIGHT_STEP = 0.5


def subtract(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def normalize(vector):
    length = math.sqrt(dot(vector, vector))

    return (vector[0] / length, vector[1] / length, vector[2] / length)


def tint(color, amount):
    return (color[0] * amount, color[1] * amount, color[2] * amount)


def reflect(to_light, normal):
    # R = 2 (N . L) N - L
    n_dot_l = dot(normal, to_light)

    return (
        2 * n_dot_l * normal[0] - to_light[0],
        2 * n_dot_l * normal[1] - to_light[1],
        2 * n_dot_l * normal[2] - to_light[2],
    )


def illumination(point, normal, settings):
    to_light = normalize(subtract(settings["light"], point))
    to_viewer = normalize(subtract(VIEWER, point))
    reflected = reflect(to_light, normal)
    n_dot_l = dot(normal, to_light)
    r_dot_v = dot(reflected, to_viewer)

    ambient = settings["ka"] * AMBIENT_INTENSITY
    diffuse = settings["kd"] * LIGHT_INTENSITY * max(n_dot_l, 0)
    specular = 0.0

    # No highlight on the side of the surface that faces away from the light
    if n_dot_l > 0 and r_dot_v > 0:
        specular = settings["ks"] * LIGHT_INTENSITY * r_dot_v ** settings["n"]

    return {
        "L": to_light,
        "V": to_viewer,
        "R": reflected,
        "N.L": n_dot_l,
        "R.V": r_dot_v,
        "ambient": ambient,
        "diffuse": diffuse,
        "specular": specular,
    }


def phong_color(terms):
    # I = ka Ia Od + kd Il (N . L) Od + ks Il (R . V)^n Os
    base = terms["ambient"] + terms["diffuse"]

    return (
        base * OBJECT_COLOR[0] + terms["specular"] * SPECULAR_COLOR[0],
        base * OBJECT_COLOR[1] + terms["specular"] * SPECULAR_COLOR[1],
        base * OBJECT_COLOR[2] + terms["specular"] * SPECULAR_COLOR[2],
    )


def clamp(color):
    return tuple(min(max(channel, 0.0), 1.0) for channel in color)


def sphere_vertices():
    # Grid of points on the sphere: stack i goes from the top pole to the bottom pole,
    # slice j goes once around the vertical axis
    rows = []

    for i in range(STACKS + 1):
        phi = math.pi * i / STACKS
        row = []

        for j in range(SLICES + 1):
            theta = 2 * math.pi * j / SLICES
            row.append((
                SPHERE_RADIUS * math.sin(phi) * math.sin(theta),
                SPHERE_RADIUS * math.cos(phi),
                SPHERE_RADIUS * math.sin(phi) * math.cos(theta),
            ))

        rows.append(row)

    return rows


def vertex_colors(rows, settings):
    # The Phong model is evaluated at every vertex; OpenGL then interpolates these colours
    # across each polygon. Four colour sets: ambient, diffuse, specular and the full model
    panels = [[], [], [], []]

    for row in rows:
        colors = [[], [], [], []]

        for point in row:
            # For a sphere centred on the origin the unit normal is the point divided by the radius
            normal = tint(point, 1 / SPHERE_RADIUS)
            terms = illumination(point, normal, settings)
            colors[0].append(clamp(tint(OBJECT_COLOR, terms["ambient"])))
            colors[1].append(clamp(tint(OBJECT_COLOR, terms["diffuse"])))
            colors[2].append(clamp(tint(SPECULAR_COLOR, terms["specular"])))
            colors[3].append(clamp(phong_color(terms)))

        for panel, panel_colors in zip(panels, colors):
            panel.append(panel_colors)

    return panels


def build_display_list(rows, colors, display_list):
    glNewList(display_list, GL_COMPILE)

    for i in range(STACKS):
        glBegin(GL_QUAD_STRIP)

        for j in range(SLICES + 1):
            for k in (i, i + 1):
                glColor3f(*colors[k][j])
                glVertex3f(*rows[k][j])

        glEnd()

    glEndList()


def format_vector(vector):
    return "(" + ", ".join(f"{value:.3f}" for value in vector) + ")"


def print_sample(name, point, settings):
    normal = tint(point, 1 / SPHERE_RADIUS)
    terms = illumination(point, normal, settings)
    color = phong_color(terms)

    print(f"\n{name}: P = {format_vector(point)}")
    print(f"  N = {format_vector(normal)}")
    print(f"  L = {format_vector(terms['L'])}")
    print(f"  V = {format_vector(terms['V'])}")
    print(f"  R = 2(N.L)N - L = {format_vector(terms['R'])}")
    print(f"  N.L = {terms['N.L']:.3f}    R.V = {terms['R.V']:.3f}")
    print(f"  Ambient  = ka Ia               = {terms['ambient']:.3f}")
    print(f"  Diffuse  = kd Il max(N.L, 0)   = {terms['diffuse']:.3f}")
    print(f"  Specular = ks Il max(R.V, 0)^n = {terms['specular']:.3f}")
    print(f"  I = (ambient + diffuse) Od + specular Os = {format_vector(color)}")
    print(f"  Clamped to [0, 1] = {format_vector(clamp(color))}")


def print_report(settings):
    print("\nPhong illumination model")
    print("I = ka Ia + kd Il max(N.L, 0) + ks Il max(R.V, 0)^n")
    print(f"ka = {settings['ka']:g}, kd = {settings['kd']:g}, ks = {settings['ks']:g}, n = {settings['n']:g}")
    print(f"Ia = {AMBIENT_INTENSITY:g}, Il = {LIGHT_INTENSITY:g}")
    print(f"Light position  = {format_vector(settings['light'])}")
    print(f"Viewer position = {format_vector(VIEWER)}")
    print(f"Object colour Od = {format_vector(OBJECT_COLOR)}, specular colour Os = {format_vector(SPECULAR_COLOR)}")

    # The highlight is brightest roughly where the normal points halfway between the light and the viewer
    halfway = normalize(tuple(a + b for a, b in zip(normalize(settings["light"]), normalize(VIEWER))))

    print_sample("Point near the highlight", tint(halfway, SPHERE_RADIUS), settings)
    print_sample("Point facing the viewer", (0.0, 0.0, SPHERE_RADIUS), settings)
    print_sample("Point on the lower left", tint((-0.6, -0.5, math.sqrt(1 - 0.6 ** 2 - 0.5 ** 2)), SPHERE_RADIUS), settings)


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


def sphere_view(left, bottom):
    # Perspective camera placed at the viewer position used in the Phong model
    glViewport(left, bottom, PANEL_SIZE, PANEL_SIZE)
    glScissor(left, bottom, PANEL_SIZE, PANEL_SIZE)
    glEnable(GL_SCISSOR_TEST)
    glClearColor(*BACKGROUND, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDisable(GL_SCISSOR_TEST)
    glClearColor(1, 1, 1, 1)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30, 1, 1, 20)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(*VIEWER, 0, 0, 0, 0, 1, 0)


def read_number(prompt, default):
    text = input(f"{prompt} [{default:g}]: ").strip()

    return float(text) if text else default


def read_point(prompt, default):
    text = input(f"{prompt} [{' '.join(f'{value:g}' for value in default)}]: ").strip()

    if not text:
        return default

    return tuple(float(value) for value in text.split())


def main():
    print("Phong Illumination Model for a 3D Object")
    print("Press Enter to accept the default value shown in brackets\n")
    settings = {
        "light": read_point("Light position (x y z)", (2.5, 2.5, 4.0)),
        "ka": read_number("Ambient reflection coefficient ka", 0.2),
        "kd": read_number("Diffuse reflection coefficient kd", 0.7),
        "ks": read_number("Specular reflection coefficient ks", 0.6),
        "n": read_number("Shininess (specular exponent) n", 32),
    }

    if len(settings["light"]) != 3:
        raise SystemExit("The light position needs three values: x y z")

    for name in ("ka", "kd", "ks"):
        if not 0 <= settings[name] <= 1:
            raise SystemExit(f"{name} must be between 0 and 1")

    if settings["n"] < 1:
        raise SystemExit("The shininess n must be at least 1")

    print_report(settings)
    rows = sphere_vertices()
    titles = [
        "Ambient: ka Ia",
        "Diffuse: kd Il (N.L)",
        "Specular: ks Il (R.V)^n",
        "Phong: ambient + diffuse + specular",
    ]
    state = {"lists": None}

    def rebuild():
        if state["lists"] is None:
            state["lists"] = glGenLists(4)

        for index, colors in enumerate(vertex_colors(rows, settings)):
            build_display_list(rows, colors, state["lists"] + index)

    def display():
        width = glutGet(GLUT_WINDOW_WIDTH)
        height = glutGet(GLUT_WINDOW_HEIGHT)
        light = settings["light"]

        if state["lists"] is None:
            rebuild()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)

        for index in range(4):
            sphere_view(MARGIN + index * (PANEL_SIZE + PANEL_GAP), FOOTER_HEIGHT)
            glCallList(state["lists"] + index)

        glDisable(GL_DEPTH_TEST)
        pixel_view(width, height)

        for index, title in enumerate(titles):
            left = MARGIN + index * (PANEL_SIZE + PANEL_GAP)
            glColor3f(0, 0, 0)
            draw_text(left + (PANEL_SIZE - text_width(title)) / 2, FOOTER_HEIGHT + PANEL_SIZE + 12, title)

        glColor3f(0, 0, 0)
        draw_text(MARGIN, height - 30, "Phong Illumination Model", GLUT_BITMAP_HELVETICA_18)
        glColor3f(0.35, 0.35, 0.35)
        draw_text(
            MARGIN,
            height - 54,
            "I = ka Ia + kd Il max(N.L, 0) + ks Il max(R.V, 0)^n      "
            "N = normal, L = towards light, V = towards viewer, R = reflection of L about N",
        )
        glColor3f(0, 0, 0)
        draw_text(
            MARGIN,
            FOOTER_HEIGHT - 30,
            f"ka = {settings['ka']:g}    kd = {settings['kd']:g}    ks = {settings['ks']:g}    "
            f"shininess n = {settings['n']:g}    Light at ({light[0]:g}, {light[1]:g}, {light[2]:g})    "
            f"Viewer (camera) at ({VIEWER[0]:g}, {VIEWER[1]:g}, {VIEWER[2]:g})",
        )
        glColor3f(0.35, 0.35, 0.35)
        draw_text(
            MARGIN,
            FOOTER_HEIGHT - 60,
            "Arrow keys: move the light      + / - : double or halve the shininess n      Esc: close",
        )
        glutSwapBuffers()

    def keyboard(key, x, y):
        if key == b"\x1b":
            glutLeaveMainLoop()
        elif key in (b"+", b"="):
            settings["n"] = min(settings["n"] * 2, 512)
            rebuild()
            glutPostRedisplay()
        elif key in (b"-", b"_"):
            settings["n"] = max(settings["n"] / 2, 1)
            rebuild()
            glutPostRedisplay()

    def special_keys(key, x, y):
        moves = {
            GLUT_KEY_LEFT: (-LIGHT_STEP, 0),
            GLUT_KEY_RIGHT: (LIGHT_STEP, 0),
            GLUT_KEY_UP: (0, LIGHT_STEP),
            GLUT_KEY_DOWN: (0, -LIGHT_STEP),
        }

        if key in moves:
            x_value, y_value, z_value = settings["light"]
            settings["light"] = (x_value + moves[key][0], y_value + moves[key][1], z_value)
            rebuild()
            glutPostRedisplay()

    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Phong Illumination Model")
    glutSetOption(GLUT_ACTION_ON_WINDOW_CLOSE, GLUT_ACTION_GLUTMAINLOOP_RETURNS)
    glClearColor(1, 1, 1, 1)
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMainLoop()


if __name__ == "__main__":
    main()
