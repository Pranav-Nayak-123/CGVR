import math
import tkinter as tk


WIDTH = 900
HEIGHT = 650
MARGIN = 70
POINT_SIZE = 4


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


def make_mapper(min_x, max_x, min_y, max_y):
    graph_width = WIDTH - 2 * MARGIN
    graph_height = HEIGHT - 2 * MARGIN
    x_range = max_x - min_x
    y_range = max_y - min_y

    scale = min(graph_width / x_range, graph_height / y_range)
    used_width = x_range * scale
    used_height = y_range * scale
    left = MARGIN + (graph_width - used_width) / 2
    top = MARGIN + (graph_height - used_height) / 2

    def screen_x(x):
        return left + (x - min_x) * scale

    def screen_y(y):
        return top + (max_y - y) * scale

    return screen_x, screen_y


def draw_graph(canvas, min_x, max_x, min_y, max_y, screen_x, screen_y):
    x_step = choose_grid_step(min_x, max_x)
    y_step = choose_grid_step(min_y, max_y)

    for x in range(min_x, max_x + 1, x_step):
        sx = screen_x(x)
        canvas.create_line(sx, screen_y(min_y), sx, screen_y(max_y), fill="#dddddd")
        canvas.create_text(sx, screen_y(min_y) + 18, text=str(x), fill="#555555", font=("Arial", 8))

    for y in range(min_y, max_y + 1, y_step):
        sy = screen_y(y)
        canvas.create_line(screen_x(min_x), sy, screen_x(max_x), sy, fill="#dddddd")
        canvas.create_text(screen_x(min_x) - 22, sy, text=str(y), fill="#555555", font=("Arial", 8))

    canvas.create_rectangle(screen_x(min_x), screen_y(max_y), screen_x(max_x), screen_y(min_y), outline="black")

    if min_y <= 0 <= max_y:
        canvas.create_line(screen_x(min_x), screen_y(0), screen_x(max_x), screen_y(0), fill="black", width=2)

    if min_x <= 0 <= max_x:
        canvas.create_line(screen_x(0), screen_y(min_y), screen_x(0), screen_y(max_y), fill="black", width=2)

    canvas.create_text(screen_x(max_x) + 18, screen_y(min_y), text="X", fill="black", font=("Arial", 10, "bold"))
    canvas.create_text(screen_x(min_x), screen_y(max_y) - 18, text="Y", fill="black", font=("Arial", 10, "bold"))


def draw_shape(canvas, points, screen_x, screen_y, color, dashed):
    edges = len(points) if len(points) > 2 else 1

    for i in range(edges):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]

        if dashed:
            canvas.create_line(
                screen_x(x1), screen_y(y1), screen_x(x2), screen_y(y2), fill=color, width=2, dash=(6, 4)
            )
        else:
            canvas.create_line(screen_x(x1), screen_y(y1), screen_x(x2), screen_y(y2), fill=color, width=2)


def plot_points(canvas, points, screen_x, screen_y, color):
    for x, y in points:
        sx = screen_x(x)
        sy = screen_y(y)

        canvas.create_oval(
            sx - POINT_SIZE,
            sy - POINT_SIZE,
            sx + POINT_SIZE,
            sy + POINT_SIZE,
            fill=color,
            outline=color,
        )
        canvas.create_text(sx + 30, sy - 10, text=f"({x:g}, {y:g})", fill=color, font=("Arial", 8))


def draw_legend(canvas, name):
    canvas.create_text(MARGIN, 22, text=name, anchor="w", fill="black", font=("Arial", 12, "bold"))
    canvas.create_text(MARGIN, 44, text="blue dashed = original", anchor="w", fill="blue", font=("Arial", 9))
    canvas.create_text(MARGIN + 170, 44, text="red solid = transformed", anchor="w", fill="red", font=("Arial", 9))


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
screen_x, screen_y = make_mapper(min_x, max_x, min_y, max_y)

window = tk.Tk()
window.title("2D Transformations using Homogeneous Coordinates")

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

draw_graph(canvas, min_x, max_x, min_y, max_y, screen_x, screen_y)
draw_shape(canvas, original, screen_x, screen_y, "blue", True)
draw_shape(canvas, transformed, screen_x, screen_y, "red", False)
plot_points(canvas, original, screen_x, screen_y, "blue")
plot_points(canvas, transformed, screen_x, screen_y, "red")
draw_legend(canvas, name)

window.mainloop()
