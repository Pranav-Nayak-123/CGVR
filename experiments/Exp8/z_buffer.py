"""Experiment 8 (lab manual Experiment 6): Z-buffer (depth buffer) algorithm for hidden surface removal."""

import math
import tkinter as tk


PANEL_SIZE = 300
PANEL_GAP = 25
MARGIN = 30
TITLE_HEIGHT = 90
FOOTER_HEIGHT = 120
WIDTH = 3 * PANEL_SIZE + 2 * PANEL_GAP + 2 * MARGIN
HEIGHT = TITLE_HEIGHT + PANEL_SIZE + FOOTER_HEIGHT
SCALE = 70
BACKGROUND = "#14141e"
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
    red, green, blue = (int(channel * brightness) for channel in color)

    return f"#{red:02x}{green:02x}{blue:02x}"


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


def scan_convert_face(points, color, face_index, frame, depth, owner, use_depth_test):
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

            if not use_depth_test or z < depth[row][column]:
                depth[row][column] = z
                frame[row][column] = color
                owner[row][column] = face_index
                written += 1

            z += step

    return tested, written


def render(faces, yaw, pitch, use_depth_test):
    # Frame buffer starts with the background colour and the depth buffer with the
    # farthest possible depth (infinity)
    frame = [[BACKGROUND] * PANEL_SIZE for _ in range(PANEL_SIZE)]
    depth = [[math.inf] * PANEL_SIZE for _ in range(PANEL_SIZE)]
    owner = [[None] * PANEL_SIZE for _ in range(PANEL_SIZE)]
    counts = []

    for index, face in enumerate(faces):
        points = [to_screen(rotate_view(point, yaw, pitch)) for point in face["points"]]
        counts.append(scan_convert_face(points, face["color"], index, frame, depth, owner, use_depth_test))

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


def depth_to_colors(depth):
    values = [z for row in depth for z in row if z != math.inf]
    nearest = min(values)
    span = (max(values) - nearest) or 1
    rows = []

    for row in depth:
        colors = []

        for z in row:
            if z == math.inf:
                colors.append("#000000")
            else:
                # Nearest surface is brightest, farthest visible surface is dark grey
                level = int(235 - 175 * (z - nearest) / span)
                colors.append(f"#{level:02x}{level:02x}{level:02x}")

        rows.append(colors)

    return rows


def make_image(pixels):
    image = tk.PhotoImage(width=PANEL_SIZE, height=PANEL_SIZE)
    image.put(" ".join("{" + " ".join(row) + "}" for row in pixels))

    return image


def draw_legend(canvas, y):
    items = [("Cube", CUBE_COLOR), ("Pyramid", PYRAMID_COLOR), ("Slanted plate", PLATE_COLOR)]
    x = MARGIN

    for name, (red, green, blue) in items:
        canvas.create_rectangle(x, y - 6, x + 12, y + 6, fill=f"#{red:02x}{green:02x}{blue:02x}", outline="")
        canvas.create_text(x + 18, y, text=name, anchor="w", font=("Arial", 9))
        x += 120


def draw_window(canvas, faces, state):
    yaw = state["yaw"]
    pitch = state["pitch"]
    plain = render(faces, yaw, pitch, False)
    frame, depth, owner, counts = render(faces, yaw, pitch, True)
    total_tested = sum(tested for tested, written in counts)
    total_written = sum(written for tested, written in counts)

    # Tk discards images that Python no longer references, so keep them in state
    state["images"] = [make_image(plain[0]), make_image(frame), make_image(depth_to_colors(depth))]
    titles = [
        "Without Z-buffer (faces in list order)",
        "With Z-buffer (hidden surfaces removed)",
        "Depth buffer (brighter = nearer)",
    ]

    canvas.delete("all")
    canvas.create_text(
        MARGIN, 22, text="Z-Buffer Algorithm for Hidden Surface Removal", anchor="w", font=("Arial", 13, "bold")
    )
    canvas.create_text(
        MARGIN,
        46,
        text=f"For every pixel of every face: if z < depth(x, y) then depth(x, y) = z and frame(x, y) = face colour"
        f"      View: {yaw:g}° about Y, {pitch:g}° about X",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )

    for i, image in enumerate(state["images"]):
        left = MARGIN + i * (PANEL_SIZE + PANEL_GAP)
        canvas.create_text(left + PANEL_SIZE / 2, TITLE_HEIGHT - 14, text=titles[i], font=("Arial", 10, "bold"))
        canvas.create_image(left, TITLE_HEIGHT, image=image, anchor="nw")
        canvas.create_rectangle(left, TITLE_HEIGHT, left + PANEL_SIZE, TITLE_HEIGHT + PANEL_SIZE, outline="black")

    footer = TITLE_HEIGHT + PANEL_SIZE
    draw_legend(canvas, footer + 25)
    canvas.create_text(
        MARGIN,
        footer + 55,
        text=f"Depth comparisons: {total_tested}      Pixels written: {total_written}"
        f"      Rejected by the depth test: {total_tested - total_written}",
        anchor="w",
        font=("Arial", 10),
    )
    canvas.create_text(
        MARGIN,
        footer + 85,
        text="Arrow keys: rotate the view      Depth buffer size = frame buffer size = "
        f"{PANEL_SIZE} x {PANEL_SIZE}",
        anchor="w",
        fill="#555555",
        font=("Arial", 9),
    )

    return depth, owner, counts


def read_number(prompt, default):
    text = input(f"{prompt} [{default:g}]: ").strip()

    return float(text) if text else default


def main():
    print("Z-Buffer Algorithm for Hidden Surface Removal")
    print("Press Enter to accept the default value shown in brackets\n")
    state = {
        "yaw": read_number("Rotation about the Y axis in degrees", -20),
        "pitch": read_number("Rotation about the X axis in degrees", 20),
    }
    faces = build_scene()

    window = tk.Tk()
    window.title("Z-Buffer Hidden Surface Removal")
    canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
    canvas.pack()

    depth, owner, counts = draw_window(canvas, faces, state)
    print_report(faces, depth, owner, counts, state["yaw"], state["pitch"])

    def rotate(yaw_change, pitch_change):
        state["yaw"] += yaw_change
        state["pitch"] += pitch_change
        draw_window(canvas, faces, state)

    window.bind("<Left>", lambda event: rotate(-ROTATION_STEP, 0))
    window.bind("<Right>", lambda event: rotate(ROTATION_STEP, 0))
    window.bind("<Up>", lambda event: rotate(0, ROTATION_STEP))
    window.bind("<Down>", lambda event: rotate(0, -ROTATION_STEP))
    window.mainloop()


if __name__ == "__main__":
    main()
