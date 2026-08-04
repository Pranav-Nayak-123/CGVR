import tkinter as tk


WIDTH = 900
HEIGHT = 650


def put_pixel(canvas, x, y, color):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline=color)


def draw_line(canvas, x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    p = dx - dy

    while True:
        put_pixel(canvas, x1, y1, "yellow")

        if x1 == x2 and y1 == y2:
            break

        p2 = 2 * p

        if p2 > -dy:
            p -= dy
            x1 += sx

        if p2 < dx:
            p += dx
            y1 += sy


def draw_circle_pixels(canvas, xc, yc, x, y):
    put_pixel(canvas, xc + x, yc + y, "cyan")
    put_pixel(canvas, xc - x, yc + y, "cyan")
    put_pixel(canvas, xc + x, yc - y, "cyan")
    put_pixel(canvas, xc - x, yc - y, "cyan")
    put_pixel(canvas, xc + y, yc + x, "cyan")
    put_pixel(canvas, xc - y, yc + x, "cyan")
    put_pixel(canvas, xc + y, yc - x, "cyan")
    put_pixel(canvas, xc - y, yc - x, "cyan")


def draw_circle(canvas, xc, yc, radius):
    x = 0
    y = radius
    p = 3 - 2 * radius

    while x <= y:
        draw_circle_pixels(canvas, xc, yc, x, y)

        if p < 0:
            p += 4 * x + 6
        else:
            p += 4 * (x - y) + 10
            y -= 1

        x += 1


window = tk.Tk()
window.title("Bresenham Line and Circle")

canvas = tk.Canvas(window, width=WIDTH, height=HEIGHT, bg="black")
canvas.pack()

draw_line(canvas, 80, 520, 780, 120)
draw_circle(canvas, 450, 325, 180)

window.mainloop()
