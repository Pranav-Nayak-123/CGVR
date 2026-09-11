"""Experiment 8: Cohen-Sutherland line clipping algorithm."""

import tkinter as tk


INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 650
PADDING = 80


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


def cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax):
    code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
    code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)

    while True:
        if code1 == 0 and code2 == 0:
            return (x1, y1, x2, y2)

        if code1 & code2:
            return None

        outside_code = code1 if code1 != 0 else code2

        if outside_code & TOP:
            x_new = x1 + (x2 - x1) * (ymax - y1) / (y2 - y1)
            y_new = ymax
        elif outside_code & BOTTOM:
            x_new = x1 + (x2 - x1) * (ymin - y1) / (y2 - y1)
            y_new = ymin
        elif outside_code & RIGHT:
            y_new = y1 + (y2 - y1) * (xmax - x1) / (x2 - x1)
            x_new = xmax
        else:
            y_new = y1 + (y2 - y1) * (xmin - x1) / (x2 - x1)
            x_new = xmin

        if outside_code == code1:
            x1, y1 = x_new, y_new
            code1 = compute_outcode(x1, y1, xmin, ymin, xmax, ymax)
        else:
            x2, y2 = x_new, y_new
            code2 = compute_outcode(x2, y2, xmin, ymin, xmax, ymax)


def read_point(label):
    x_value, y_value = map(float, input(f"Enter {label} (x y): ").split())
    return x_value, y_value


def draw_result(x1, y1, x2, y2, xmin, ymin, xmax, ymax, clipped_line):
    values_x = [x1, x2, xmin, xmax]
    values_y = [y1, y2, ymin, ymax]
    minimum_x, maximum_x = min(values_x), max(values_x)
    minimum_y, maximum_y = min(values_y), max(values_y)
    span_x = max(maximum_x - minimum_x, 1)
    span_y = max(maximum_y - minimum_y, 1)
    minimum_x -= span_x * 0.2
    maximum_x += span_x * 0.2
    minimum_y -= span_y * 0.2
    maximum_y += span_y * 0.2

    scale_x = (CANVAS_WIDTH - 2 * PADDING) / (maximum_x - minimum_x)
    scale_y = (CANVAS_HEIGHT - 2 * PADDING) / (maximum_y - minimum_y)
    scale = min(scale_x, scale_y)

    def screen_point(x_value, y_value):
        screen_x = PADDING + (x_value - minimum_x) * scale
        screen_y = CANVAS_HEIGHT - PADDING - (y_value - minimum_y) * scale
        return screen_x, screen_y

    window = tk.Tk()
    window.title("Cohen-Sutherland Line Clipping")
    canvas = tk.Canvas(window, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
    canvas.pack()

    left, bottom = screen_point(xmin, ymin)
    right, top = screen_point(xmax, ymax)
    canvas.create_rectangle(left, top, right, bottom, outline="black", width=3)
    canvas.create_text(left, top - 15, text="Clipping window", anchor="w")

    start_x, start_y = screen_point(x1, y1)
    end_x, end_y = screen_point(x2, y2)
    canvas.create_line(start_x, start_y, end_x, end_y, fill="red", dash=(8, 4), width=2)

    if clipped_line:
        clip_x1, clip_y1, clip_x2, clip_y2 = clipped_line
        start_x, start_y = screen_point(clip_x1, clip_y1)
        end_x, end_y = screen_point(clip_x2, clip_y2)
        canvas.create_line(start_x, start_y, end_x, end_y, fill="blue", width=4)
        message = "Red dashed: original line | Blue: clipped line"
    else:
        message = "Red dashed: original line | The line is completely outside the window"

    canvas.create_text(CANVAS_WIDTH / 2, 30, text=message, font=("Arial", 12, "bold"))
    window.mainloop()


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

    clipped_line = cohen_sutherland_clip(x1, y1, x2, y2, xmin, ymin, xmax, ymax)

    if clipped_line:
        print("Accepted clipped line:")
        print(f"({clipped_line[0]:.2f}, {clipped_line[1]:.2f}) to ({clipped_line[2]:.2f}, {clipped_line[3]:.2f})")
    else:
        print("Rejected: the line lies completely outside the clipping window.")

    draw_result(x1, y1, x2, y2, xmin, ymin, xmax, ymax, clipped_line)


if __name__ == "__main__":
    main()