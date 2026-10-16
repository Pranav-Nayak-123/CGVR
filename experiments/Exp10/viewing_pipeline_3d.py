"""Experiment 10 (lab manual Experiment 10): 3D viewing pipeline with projection and viewport mapping."""

import math
import tkinter as tk


WIDTH = 900
HEIGHT = 650
VIEWPORTS = [
    {"name": "Viewport 1: perspective projection", "left": 30, "top": 115, "width": 400, "height": 400,
     "projection": "perspective"},
    {"name": "Viewport 2: orthographic (parallel) projection", "left": 470, "top": 115, "width": 400, "height": 400,
     "projection": "orthographic"},
]
UP = (0.0, 1.0, 0.0)
MODEL_TRANSLATION = (-1.0, 0.0, -1.0)
MODEL_ROTATION_Y = 30
GRID_SIZE = 3
ORBIT_STEP = 10
ZOOM_FACTOR = 0.9
TRACED_VERTEX = 8

# House in its own modeling coordinates: a 2 x 1.4 x 2 box with a roof and a door
HOUSE_VERTICES = [
    (0, 0, 2), (2, 0, 2), (2, 1.4, 2), (0, 1.4, 2),
    (0, 0, 0), (2, 0, 0), (2, 1.4, 0), (0, 1.4, 0),
    (1, 2.2, 2), (1, 2.2, 0),
    (0.7, 0, 2), (1.3, 0, 2), (1.3, 1.0, 2), (0.7, 1.0, 2),
]
WALL_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
ROOF_EDGES = [(3, 8), (2, 8), (7, 9), (6, 9), (8, 9)]
DOOR_EDGES = [(10, 13), (13, 12), (12, 11)]

# Each clipping plane keeps the points where w + sign * coordinate >= 0, that is -w <= x, y, z <= w
CLIP_PLANES = [(0, 1), (0, -1), (1, 1), (1, -1), (2, 1), (2, -1)]


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


def length(vector):
    return math.sqrt(dot(vector, vector))


def normalize(vector):
    size = length(vector)

    return (vector[0] / size, vector[1] / size, vector[2] / size)


def identity_matrix():
    return [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
    ]


def translation_matrix(tx, ty, tz):
    return [
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1],
    ]


def rotation_y_matrix(angle_in_degrees):
    angle = math.radians(angle_in_degrees)
    cos_value = math.cos(angle)
    sin_value = math.sin(angle)

    return [
        [cos_value, 0, sin_value, 0],
        [0, 1, 0, 0],
        [-sin_value, 0, cos_value, 0],
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


def transform(matrix, point):
    return tuple(sum(matrix[row][k] * point[k] for k in range(4)) for row in range(4))


def view_matrix(eye, at, up):
    # Camera axes: n points from the look-at point back towards the eye (the camera looks
    # along -n), u points to the right and v points up
    n = normalize(subtract(eye, at))
    u = normalize(cross(up, n))
    v = cross(n, u)

    # Rotation that lines up u, v, n with x, y, z, combined with a translation of the eye to the origin
    matrix = [
        [u[0], u[1], u[2], -dot(u, eye)],
        [v[0], v[1], v[2], -dot(v, eye)],
        [n[0], n[1], n[2], -dot(n, eye)],
        [0, 0, 0, 1],
    ]

    return matrix, (u, v, n)


def perspective_matrix(fov, aspect, near, far):
    f = 1 / math.tan(math.radians(fov) / 2)

    return [
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (far + near) / (near - far), 2 * far * near / (near - far)],
        [0, 0, -1, 0],
    ]


def orthographic_matrix(half_width, half_height, near, far):
    return [
        [1 / half_width, 0, 0, 0],
        [0, 1 / half_height, 0, 0],
        [0, 0, -2 / (far - near), -(far + near) / (far - near)],
        [0, 0, 0, 1],
    ]


def viewport_matrix(left, top, width, height):
    # NDC x in [-1, 1] maps to [left, left + width], NDC y in [-1, 1] maps to [bottom, top]
    # (screen y grows downwards) and NDC z in [-1, 1] maps to the depth range [0, 1]
    return [
        [width / 2, 0, 0, left + width / 2],
        [0, -height / 2, 0, top + height / 2],
        [0, 0, 0.5, 0.5],
        [0, 0, 0, 1],
    ]


def build_pipeline(camera, viewport):
    model = multiply_matrices(rotation_y_matrix(MODEL_ROTATION_Y), translation_matrix(*MODEL_TRANSLATION))
    view, axes = view_matrix(camera["eye"], camera["at"], UP)
    aspect = viewport["width"] / viewport["height"]

    if viewport["projection"] == "perspective":
        projection = perspective_matrix(camera["fov"], aspect, camera["near"], camera["far"])
    else:
        # Parallel view volume sized to what the perspective camera sees at the look-at point
        half_height = length(subtract(camera["eye"], camera["at"])) * math.tan(math.radians(camera["fov"]) / 2)
        projection = orthographic_matrix(half_height * aspect, half_height, camera["near"], camera["far"])

    return {
        "model": model,
        "view": view,
        "projection": projection,
        "viewport": viewport_matrix(viewport["left"], viewport["top"], viewport["width"], viewport["height"]),
        "axes": axes,
    }


def house_stages(pipeline, point):
    modeling = (point[0], point[1], point[2], 1)
    world = transform(pipeline["model"], modeling)
    eye = transform(pipeline["view"], world)
    clip = transform(pipeline["projection"], eye)
    ndc = (clip[0] / clip[3], clip[1] / clip[3], clip[2] / clip[3], 1)
    screen = transform(pipeline["viewport"], ndc)

    return {"modeling": modeling, "world": world, "eye": eye, "clip": clip, "ndc": ndc, "screen": screen}


def to_clip(pipeline, world_point):
    eye = transform(pipeline["view"], (world_point[0], world_point[1], world_point[2], 1))

    return transform(pipeline["projection"], eye)


def to_screen(pipeline, clip):
    # Perspective division gives normalized device coordinates, then the viewport transformation
    ndc = (clip[0] / clip[3], clip[1] / clip[3], clip[2] / clip[3], 1)
    screen = transform(pipeline["viewport"], ndc)

    return screen[0], screen[1]


def inside_view_volume(clip):
    return all(clip[3] + sign * clip[axis] >= 0 for axis, sign in CLIP_PLANES)


def clip_line(start, end):
    # Parametric (Liang-Barsky) clipping in homogeneous clip coordinates, done before the
    # division by w so that points behind the camera are removed correctly
    t_enter = 0.0
    t_exit = 1.0

    for axis, sign in CLIP_PLANES:
        d_start = start[3] + sign * start[axis]
        d_end = end[3] + sign * end[axis]

        if d_start < 0 and d_end < 0:
            return None

        if d_start < 0:
            t_enter = max(t_enter, d_start / (d_start - d_end))
        elif d_end < 0:
            t_exit = min(t_exit, d_start / (d_start - d_end))

    if t_enter > t_exit:
        return None

    def point_at(t):
        return tuple(a + t * (b - a) for a, b in zip(start, end))

    return point_at(t_enter), point_at(t_exit)


def clean(value):
    if abs(value) < 1e-9:
        return 0.0

    return value


def format_point(values, digits=3):
    return "(" + ", ".join(f"{clean(value):.{digits}f}" for value in values) + ")"


def print_matrix(title, matrix):
    print(f"\n{title}")

    for row in matrix:
        print("  ".join(f"{clean(value):9.4f}" for value in row))


def print_report(camera):
    perspective = build_pipeline(camera, VIEWPORTS[0])
    orthographic = build_pipeline(camera, VIEWPORTS[1])
    u, v, n = perspective["axes"]

    print(
        f"\nStage 1: Modeling transformation M = Ry({MODEL_ROTATION_Y:g}) x T{format_point(MODEL_TRANSLATION, 0)}"
        "  (modeling -> world coordinates)"
    )
    print_matrix("M", perspective["model"])

    print("\nStage 2: Viewing transformation V  (world -> camera coordinates)")
    print(f"eye = {format_point(camera['eye'], 2)}, look-at = {format_point(camera['at'], 2)}, up = {format_point(UP, 2)}")
    print(f"n = (eye - look-at) / |eye - look-at| = {format_point(n)}")
    print(f"u = (up x n) / |up x n|               = {format_point(u)}")
    print(f"v = n x u                             = {format_point(v)}")
    print_matrix("V", perspective["view"])

    print(f"\nStage 3: Projection (camera -> clip coordinates), near = {camera['near']:g}, far = {camera['far']:g}")
    print_matrix(f"P perspective (fov = {camera['fov']:g} degrees, aspect = 1)", perspective["projection"])
    print_matrix("P orthographic (same visible size at the look-at point)", orthographic["projection"])

    print("\nStage 4: Clipping against -w <= x, y, z <= w, then perspective division (x/w, y/w, z/w) -> NDC")

    print("\nStage 5: Viewport transformation (NDC -> screen coordinates)")
    for viewport, pipeline in zip(VIEWPORTS, (perspective, orthographic)):
        print_matrix(
            f"{viewport['name']}: x = {viewport['left']}, y = {viewport['top']}, "
            f"width = {viewport['width']}, height = {viewport['height']}",
            pipeline["viewport"],
        )

    composite = multiply_matrices(perspective["projection"], multiply_matrices(perspective["view"], perspective["model"]))
    print_matrix("Composite matrix for the perspective view: P x V x M", composite)

    print(f"\nVertex {TRACED_VERTEX} (front roof peak) through the pipeline")
    first = house_stages(perspective, HOUSE_VERTICES[TRACED_VERTEX])
    second = house_stages(orthographic, HOUSE_VERTICES[TRACED_VERTEX])
    print(f"{'Stage':<22}{'Perspective':<40}{'Orthographic'}")
    # (label, stage, number of coordinates to show, decimal places)
    rows = [
        ("Modeling", "modeling", 3, 2),
        ("World", "world", 3, 3),
        ("Camera", "eye", 3, 3),
        ("Clip (x, y, z, w)", "clip", 4, 3),
        ("NDC", "ndc", 3, 3),
        ("Screen (x, y, depth)", "screen", 3, 2),
    ]

    for label, key, count, digits in rows:
        print(f"{label:<22}{format_point(first[key][:count], digits):<40}{format_point(second[key][:count], digits)}")

    print(f"\n{'Vertex':<8}{'World coordinates':<28}{'Perspective screen':<24}{'Orthographic screen'}")

    for index, point in enumerate(HOUSE_VERTICES):
        columns = []

        for pipeline in (perspective, orthographic):
            stages = house_stages(pipeline, point)
            columns.append(format_point(stages["screen"][:2], 1) if inside_view_volume(stages["clip"]) else "clipped")

        world = house_stages(perspective, point)["world"]
        print(f"{index:<8}{format_point(world[:3], 2):<28}{columns[0]:<24}{columns[1]}")


def draw_line(canvas, pipeline, start, end, color, width):
    clipped = clip_line(to_clip(pipeline, start), to_clip(pipeline, end))

    if clipped is None:
        return

    x1, y1 = to_screen(pipeline, clipped[0])
    x2, y2 = to_screen(pipeline, clipped[1])
    canvas.create_line(x1, y1, x2, y2, fill=color, width=width)


def draw_viewport(canvas, camera, viewport):
    pipeline = build_pipeline(camera, viewport)
    left = viewport["left"]
    top = viewport["top"]
    right = left + viewport["width"]
    bottom = top + viewport["height"]

    canvas.create_rectangle(left, top, right, bottom, fill="#f8f9fc", outline="")
    label = viewport["name"]

    if viewport["projection"] == "perspective":
        label += f" (fov {camera['fov']:g}°)"

    canvas.create_text(left, top - 14, text=label, anchor="w", font=("Arial", 10, "bold"))
    canvas.create_text(
        left,
        bottom + 14,
        text=f"x = {left}, y = {top}, width = {viewport['width']}, height = {viewport['height']}",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )

    # Ground grid on the plane y = 0, in world coordinates
    for i in range(-GRID_SIZE, GRID_SIZE + 1):
        draw_line(canvas, pipeline, (i, 0, -GRID_SIZE), (i, 0, GRID_SIZE), "#c9ccd6", 1)
        draw_line(canvas, pipeline, (-GRID_SIZE, 0, i), (GRID_SIZE, 0, i), "#c9ccd6", 1)

    world = [house_stages(pipeline, point)["world"] for point in HOUSE_VERTICES]

    for edges, color, width in ((WALL_EDGES, "#1d3557", 2), (ROOF_EDGES, "#c1440e", 2), (DOOR_EDGES, "#7a5c3a", 1)):
        for a, b in edges:
            draw_line(canvas, pipeline, world[a], world[b], color, width)

    clip = to_clip(pipeline, world[TRACED_VERTEX])

    if inside_view_volume(clip):
        x, y = to_screen(pipeline, clip)
        canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="red", outline="red")
        canvas.create_text(x + 8, y - 10, text=f"V{TRACED_VERTEX}", fill="red", anchor="w", font=("Arial", 9, "bold"))

    canvas.create_rectangle(left, top, right, bottom, outline="black", width=2)


def draw_window(canvas, camera):
    eye = camera["eye"]
    at = camera["at"]

    canvas.delete("all")
    canvas.create_text(30, 24, text="3D Viewing Pipeline", anchor="w", font=("Arial", 13, "bold"))
    canvas.create_text(
        30,
        50,
        text="Modeling coords -> (M) -> World -> (V) -> Camera -> (P) -> Clip -> clipping, divide by w -> NDC"
        " -> (viewport) -> Screen",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )

    for viewport in VIEWPORTS:
        draw_viewport(canvas, camera, viewport)

    canvas.create_text(
        30,
        HEIGHT - 70,
        text=f"Eye ({eye[0]:.2f}, {eye[1]:.2f}, {eye[2]:.2f})    Look-at ({at[0]:g}, {at[1]:g}, {at[2]:g})    "
        f"Up (0, 1, 0)    Near {camera['near']:g}    Far {camera['far']:g}",
        anchor="w",
        font=("Arial", 10),
    )
    canvas.create_text(
        30,
        HEIGHT - 42,
        text=f"Arrow keys: orbit the camera      + / - : move closer / farther      "
        f"Red dot: vertex {TRACED_VERTEX} traced in the console",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )


def orbit(camera, azimuth_change, elevation_change, zoom):
    offset = subtract(camera["eye"], camera["at"])
    radius = max(length(offset) * zoom, 0.5)
    azimuth = math.radians(math.degrees(math.atan2(offset[0], offset[2])) + azimuth_change)
    elevation = math.degrees(math.asin(offset[1] / length(offset))) + elevation_change
    elevation = math.radians(min(max(elevation, -85), 85))
    at = camera["at"]

    camera["eye"] = (
        at[0] + radius * math.cos(elevation) * math.sin(azimuth),
        at[1] + radius * math.sin(elevation),
        at[2] + radius * math.cos(elevation) * math.cos(azimuth),
    )


def read_number(prompt, default):
    text = input(f"{prompt} [{default:g}]: ").strip()

    return float(text) if text else default


def read_point(prompt, default):
    text = input(f"{prompt} [{' '.join(f'{value:g}' for value in default)}]: ").strip()

    if not text:
        return default

    values = tuple(float(value) for value in text.split())

    if len(values) != 3:
        raise SystemExit("Enter three values: x y z")

    return values


def main():
    print("3D Viewing Pipeline with Projection and Viewport Mapping")
    print("Press Enter to accept the default value shown in brackets\n")
    camera = {
        "eye": read_point("Camera position (eye) x y z", (5.0, 2.5, 1.5)),
        "at": read_point("Look-at point x y z", (0.0, 1.0, 0.0)),
        "fov": read_number("Field of view in degrees", 60),
        "near": read_number("Near plane distance", 1),
        "far": read_number("Far plane distance", 20),
    }

    view_direction = subtract(camera["eye"], camera["at"])

    if length(view_direction) < 1e-9:
        raise SystemExit("The eye and the look-at point must be different")
    if length(cross(UP, view_direction)) < 1e-9:
        raise SystemExit("The viewing direction cannot be parallel to the up vector (0, 1, 0)")
    if not 0 < camera["fov"] < 180:
        raise SystemExit("The field of view must be between 0 and 180 degrees")
    if not 0 < camera["near"] < camera["far"]:
        raise SystemExit("Need 0 < near < far")

    print_report(camera)

    window = tk.Tk()
    window.title("3D Viewing Pipeline")
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
    canvas.pack()
    draw_window(canvas, camera)

    def move_camera(azimuth_change, elevation_change, zoom):
        orbit(camera, azimuth_change, elevation_change, zoom)
        draw_window(canvas, camera)

    window.bind("<Left>", lambda event: move_camera(-ORBIT_STEP, 0, 1))
    window.bind("<Right>", lambda event: move_camera(ORBIT_STEP, 0, 1))
    window.bind("<Up>", lambda event: move_camera(0, ORBIT_STEP, 1))
    window.bind("<Down>", lambda event: move_camera(0, -ORBIT_STEP, 1))

    for key in ("<plus>", "<equal>", "<KP_Add>"):
        window.bind(key, lambda event: move_camera(0, 0, ZOOM_FACTOR))

    for key in ("<minus>", "<KP_Subtract>"):
        window.bind(key, lambda event: move_camera(0, 0, 1 / ZOOM_FACTOR))

    window.mainloop()


if __name__ == "__main__":
    main()
