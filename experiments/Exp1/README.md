# Experiment 1: Implementation of DDA and Bresenham Line Drawing Algorithms

## Aim

To implement the Digital Differential Analyzer (DDA) algorithm and Bresenham's Line Drawing Algorithm for
generating straight lines on a raster display using OpenGL.

## Course Outcome

**CO1:** Understand the principles of graphics systems, graphics primitives, and raster graphics algorithms.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to:

- Understand raster scan graphics.
- Differentiate between DDA and Bresenham algorithms.
- Draw straight lines using incremental techniques.
- Compare floating-point and integer arithmetic algorithms.
- Analyze the computational efficiency of line drawing algorithms.

## Theory

A raster display is a grid of pixels, so a line from `(x1, y1)` to `(x2, y2)` has to be approximated by the
pixels closest to the ideal line. Both algorithms step along the line one pixel at a time (incremental methods).

**DDA (Digital Differential Analyzer)**

```text
dx = x2 - x1,  dy = y2 - y1,  steps = max(|dx|, |dy|)
x_increment = dx / steps,  y_increment = dy / steps
x(k+1) = x(k) + x_increment,  y(k+1) = y(k) + y_increment,  pixel = (round(x), round(y))
```

DDA needs floating-point additions and a rounding at every step.

**Bresenham's algorithm** uses only integers. The program uses the general form that works for every slope:

```text
dx = |x2 - x1|,  dy = |y2 - y1|,  sx = ±1,  sy = ±1,  e = dx - dy
repeat: plot (x, y); if 2e > -dy then e = e - dy, x = x + sx; if 2e < dx then e = e + dx, y = y + sy
```

The error term `e` measures which neighbouring pixel is closer to the ideal line, so only integer additions,
subtractions and comparisons are needed.

| | DDA | Bresenham |
| --- | --- | --- |
| Arithmetic | Floating point (division, addition, rounding) | Integer only |
| Speed | Slower (floating point and rounding every step) | Faster |
| Accuracy | Rounding errors can build up over long lines | Exact integer decisions |
| Ties (line exactly half way between two pixels) | Rounds 0.5 up | Decided by the error term, so it may pick the other pixel |

## Algorithm

**DDA**

1. Read the end points `(x1, y1)` and `(x2, y2)`.
2. Compute `dx`, `dy` and `steps = max(|dx|, |dy|)`.
3. Compute `x_increment = dx / steps` and `y_increment = dy / steps`.
4. Start with `x = x1`, `y = y1`. Repeat `steps + 1` times: plot `(round(x), round(y))`, then add the increments.

**Bresenham**

1. Read the end points. Compute `dx = |x2 - x1|`, `dy = |y2 - y1|`, the step directions `sx`, `sy` and `e = dx - dy`.
2. Plot `(x, y)`. Stop if it is the end point.
3. If `2e > -dy`, subtract `dy` from `e` and move `x` by `sx`.
4. If `2e < dx`, add `dx` to `e` and move `y` by `sy`. Go to step 2.

## Program

`dda_bresenham.py` reads the two end points, runs both algorithms and prints:

- the DDA table (step, real x and y, rounded pixel),
- the Bresenham table (step, pixel, error term `e`),
- a comparison of the work done and of the pixels chosen differently by the two algorithms.

The OpenGL window shows the two results side by side using two viewports. Each raster pixel is drawn as a
filled square on the pixel grid, with the ideal line drawn over it in black.

## Run

```powershell
pip install PyOpenGL
python dda_bresenham.py
```

Sample input:

```text
x1: 2
y1: 3
x2: 12
y2: 8
```

Esc closes the window.

## Result

The DDA and Bresenham line drawing algorithms were implemented in OpenGL and the generated pixels were
displayed and compared.
