import tkinter as tk


WIDTH = 900
HEIGHT = 650
MARGIN = 70
POINT_SIZE = 4


def bresenham_line(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    p = dx - dy
    points = []

    while True:
        points.append((x1, y1))

        if x1 == x2 and y1 == y2:
            break

        p2 = 2 * p

        if p2 > -dy:
            p -= dy
            x1 += sx

        if p2 < dx:
            p += dx
            y1 += sy

    return points


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


def draw_connected_line(canvas, points, screen_x, screen_y):
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        canvas.create_line(screen_x(x1), screen_y(y1), screen_x(x2), screen_y(y2), fill="red", width=2)


def plot_points(canvas, points, screen_x, screen_y):
    for x, y in points:
        sx = screen_x(x)
        sy = screen_y(y)

        canvas.create_oval(
            sx - POINT_SIZE,
            sy - POINT_SIZE,
            sx + POINT_SIZE,
            sy + POINT_SIZE,
            fill="blue",
            outline="blue",
        )
        canvas.create_text(sx + 24, sy - 10, text=f"({x}, {y})", fill="black", font=("Arial", 8))


print("Enter Bresenham line coordinates")
x1 = int(input("x1: "))
y1 = int(input("y1: "))
x2 = int(input("x2: "))
y2 = int(input("y2: "))

points = bresenham_line(x1, y1, x2, y2)
min_x, max_x, min_y, max_y = get_graph_bounds(points)
screen_x, screen_y = make_mapper(min_x, max_x, min_y, max_y)

print("\nBresenham line points:")
for x, y in points:
    print(x, y)

window = tk.Tk()
window.title("Bresenham Line on Auto-Scaled Graph")

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

draw_graph(canvas, min_x, max_x, min_y, max_y, screen_x, screen_y)
draw_connected_line(canvas, points, screen_x, screen_y)
plot_points(canvas, points, screen_x, screen_y)

window.mainloop()
