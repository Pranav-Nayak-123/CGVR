import tkinter as tk


WIDTH = 900
HEIGHT = 650
SCALE = 20
ORIGIN_X = WIDTH // 2
ORIGIN_Y = HEIGHT // 2


def graph_x(x):
    return ORIGIN_X + x * SCALE


def graph_y(y):
    return ORIGIN_Y - y * SCALE


def draw_graph(canvas):
    for x in range(0, WIDTH, SCALE):
        canvas.create_line(x, 0, x, HEIGHT, fill="#dddddd")

    for y in range(0, HEIGHT, SCALE):
        canvas.create_line(0, y, WIDTH, y, fill="#dddddd")

    canvas.create_line(0, ORIGIN_Y, WIDTH, ORIGIN_Y, fill="black", width=2)
    canvas.create_line(ORIGIN_X, 0, ORIGIN_X, HEIGHT, fill="black", width=2)

    canvas.create_text(WIDTH - 15, ORIGIN_Y - 12, text="X", fill="black")
    canvas.create_text(ORIGIN_X + 12, 15, text="Y", fill="black")


def plot_point(canvas, x, y):
    screen_x = graph_x(x)
    screen_y = graph_y(y)
    canvas.create_oval(
        screen_x - 3,
        screen_y - 3,
        screen_x + 3,
        screen_y + 3,
        fill="blue",
        outline="blue",
    )


def dda_line(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        return [(x1, y1)]

    x_increment = dx / steps
    y_increment = dy / steps
    x = x1
    y = y1
    points = []

    for i in range(steps + 1):
        points.append((round(x), round(y)))
        x += x_increment
        y += y_increment

    return points


print("Enter DDA line coordinates")
x1 = int(input("x1: "))
y1 = int(input("y1: "))
x2 = int(input("x2: "))
y2 = int(input("y2: "))

points = dda_line(x1, y1, x2, y2)

print("\nDDA points:")
for x, y in points:
    print(x, y)

window = tk.Tk()
window.title("DDA Line on Graph")

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

draw_graph(canvas)

for x, y in points:
    plot_point(canvas, x, y)

window.mainloop()
