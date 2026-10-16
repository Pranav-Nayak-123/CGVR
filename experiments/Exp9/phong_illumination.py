"""Experiment 9 (lab manual Experiment 7): Phong illumination model for a 3D object (sphere)."""

import math
import tkinter as tk


PANEL_SIZE = 230
PANEL_GAP = 20
MARGIN = 30
TITLE_HEIGHT = 95
FOOTER_HEIGHT = 110
WIDTH = 4 * PANEL_SIZE + 3 * PANEL_GAP + 2 * MARGIN
HEIGHT = TITLE_HEIGHT + PANEL_SIZE + FOOTER_HEIGHT
BACKGROUND = "#14141e"

SPHERE_RADIUS = 1.0
VIEW_HALF_SIZE = 1.25
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


def reflect(to_light, normal):
    # R = 2 (N . L) N - L
    n_dot_l = dot(normal, to_light)

    return (
        2 * n_dot_l * normal[0] - to_light[0],
        2 * n_dot_l * normal[1] - to_light[1],
        2 * n_dot_l * normal[2] - to_light[2],
    )


def sphere_point(x, y):
    # Visible point of the sphere (centred on the origin) seen along the z axis
    remaining = SPHERE_RADIUS * SPHERE_RADIUS - x * x - y * y

    if remaining < 0:
        return None

    return (x, y, math.sqrt(remaining))


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


def to_hex(color):
    red, green, blue = (int(255 * min(max(channel, 0), 1) + 0.5) for channel in color)

    return f"#{red:02x}{green:02x}{blue:02x}"


def tint(color, amount):
    return (color[0] * amount, color[1] * amount, color[2] * amount)


def phong_color(terms):
    # I = ka Ia Od + kd Il (N . L) Od + ks Il (R . V)^n Os
    base = terms["ambient"] + terms["diffuse"]

    return (
        base * OBJECT_COLOR[0] + terms["specular"] * SPECULAR_COLOR[0],
        base * OBJECT_COLOR[1] + terms["specular"] * SPECULAR_COLOR[1],
        base * OBJECT_COLOR[2] + terms["specular"] * SPECULAR_COLOR[2],
    )


def render(settings):
    # Four images: ambient only, diffuse only, specular only, and the full Phong model
    panels = [[], [], [], []]

    for row in range(PANEL_SIZE):
        y = VIEW_HALF_SIZE * (1 - 2 * (row + 0.5) / PANEL_SIZE)
        rows = [[], [], [], []]

        for column in range(PANEL_SIZE):
            x = VIEW_HALF_SIZE * (2 * (column + 0.5) / PANEL_SIZE - 1)
            point = sphere_point(x, y)

            if point is None:
                for colors in rows:
                    colors.append(BACKGROUND)
                continue

            # For a sphere centred on the origin the unit normal is the point divided by the radius
            normal = tint(point, 1 / SPHERE_RADIUS)
            terms = illumination(point, normal, settings)
            rows[0].append(to_hex(tint(OBJECT_COLOR, terms["ambient"])))
            rows[1].append(to_hex(tint(OBJECT_COLOR, terms["diffuse"])))
            rows[2].append(to_hex(tint(SPECULAR_COLOR, terms["specular"])))
            rows[3].append(to_hex(phong_color(terms)))

        for panel, colors in zip(panels, rows):
            panel.append(colors)

    return panels


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
    print(f"  Clamped to [0, 1] and shown as {to_hex(color)}")


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


def make_image(pixels):
    image = tk.PhotoImage(width=PANEL_SIZE, height=PANEL_SIZE)
    image.put(" ".join("{" + " ".join(row) + "}" for row in pixels))

    return image


def draw_window(canvas, settings, state):
    light = settings["light"]

    # Tk discards images that Python no longer references, so keep them in state
    state["images"] = [make_image(panel) for panel in render(settings)]
    titles = [
        "Ambient: ka Ia",
        "Diffuse: kd Il (N.L)",
        "Specular: ks Il (R.V)^n",
        "Phong: ambient + diffuse + specular",
    ]

    canvas.delete("all")
    canvas.create_text(MARGIN, 22, text="Phong Illumination Model", anchor="w", font=("Arial", 13, "bold"))
    canvas.create_text(
        MARGIN,
        46,
        text="I = ka Ia + kd Il max(N.L, 0) + ks Il max(R.V, 0)^n      "
        "N = surface normal, L = towards light, V = towards viewer, R = reflection of L about N",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )

    radius = SPHERE_RADIUS / VIEW_HALF_SIZE * PANEL_SIZE / 2

    for i, image in enumerate(state["images"]):
        left = MARGIN + i * (PANEL_SIZE + PANEL_GAP)
        centre_x = left + PANEL_SIZE / 2
        centre_y = TITLE_HEIGHT + PANEL_SIZE / 2
        canvas.create_text(centre_x, TITLE_HEIGHT - 14, text=titles[i], font=("Arial", 10, "bold"))
        canvas.create_image(left, TITLE_HEIGHT, image=image, anchor="nw")
        canvas.create_rectangle(left, TITLE_HEIGHT, left + PANEL_SIZE, TITLE_HEIGHT + PANEL_SIZE, outline="black")

        if i < 3:
            # Faint outline so the sphere is visible even where a single term is zero
            canvas.create_oval(
                centre_x - radius, centre_y - radius, centre_x + radius, centre_y + radius, outline="#3c3c50"
            )

    footer = TITLE_HEIGHT + PANEL_SIZE
    canvas.create_text(
        MARGIN,
        footer + 30,
        text=f"ka = {settings['ka']:g}    kd = {settings['kd']:g}    ks = {settings['ks']:g}    "
        f"shininess n = {settings['n']:g}    Light at ({light[0]:g}, {light[1]:g}, {light[2]:g})    "
        f"Viewer at ({VIEWER[0]:g}, {VIEWER[1]:g}, {VIEWER[2]:g})",
        anchor="w",
        font=("Arial", 10),
    )
    canvas.create_text(
        MARGIN,
        footer + 60,
        text="Arrow keys: move the light      + / - : double or halve the shininess n",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )


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

    window = tk.Tk()
    window.title("Phong Illumination Model")
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
    canvas.pack()
    state = {}
    draw_window(canvas, settings, state)

    def move_light(dx, dy):
        x, y, z = settings["light"]
        settings["light"] = (x + dx, y + dy, z)
        draw_window(canvas, settings, state)

    def change_shininess(factor):
        settings["n"] = min(max(settings["n"] * factor, 1), 512)
        draw_window(canvas, settings, state)

    window.bind("<Left>", lambda event: move_light(-LIGHT_STEP, 0))
    window.bind("<Right>", lambda event: move_light(LIGHT_STEP, 0))
    window.bind("<Up>", lambda event: move_light(0, LIGHT_STEP))
    window.bind("<Down>", lambda event: move_light(0, -LIGHT_STEP))

    for key in ("<plus>", "<equal>", "<KP_Add>"):
        window.bind(key, lambda event: change_shininess(2))

    for key in ("<minus>", "<KP_Subtract>"):
        window.bind(key, lambda event: change_shininess(0.5))

    window.mainloop()


if __name__ == "__main__":
    main()
