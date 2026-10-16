# Experiment 2: Implementation of Midpoint Circle Drawing Algorithm

## Aim

To implement the Midpoint Circle Drawing Algorithm for generating a circle on a raster display using OpenGL by
exploiting the eight-way symmetry of a circle.

## Course Outcome

**CO1:** Understand and implement fundamental computer graphics algorithms for raster displays.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, students will be able to:

- Understand the mathematical representation of circles.
- Apply the Midpoint Circle Drawing Algorithm.
- Utilize the eight-way symmetry property of circles.
- Compare circle generation techniques.
- Develop OpenGL programs for circle rendering.

## Theory

A circle with centre `(xc, yc)` and radius `r` is the set of points with `(x - xc)² + (y - yc)² = r²`. Computing
`y = ±sqrt(r² - x²)` for every x is slow and leaves gaps, and the polar form needs sin and cos.

**Eight-way symmetry:** if `(x, y)` is on a circle centred at the origin, so are `(y, x)`, `(-x, y)`, `(-y, x)`,
`(-x, -y)`, `(-y, -x)`, `(x, -y)` and `(y, -x)`. So only one octant (from `(0, r)` until `x >= y`) has to be
computed, and every point gives eight pixels.

**Midpoint method:** the circle function `f(x, y) = x² + y² - r²` is negative inside the circle and positive
outside. At each step x increases by 1, and the sign of `f` at the midpoint between the two candidate pixels
`(x + 1, y)` and `(x + 1, y - 1)` decides which one is closer to the circle. This gives an integer decision parameter:

```text
p0 = 1 - r
if p(k) < 0:  next pixel (x + 1, y),      p(k+1) = p(k) + 2x(k+1) + 1
else:         next pixel (x + 1, y - 1),  p(k+1) = p(k) + 2x(k+1) + 1 - 2y(k+1)
```

## Algorithm

1. Read the centre `(xc, yc)` and the radius `r`.
2. Set `x = 0`, `y = r`, `p = 1 - r`, and plot the eight symmetric points of `(x, y)`.
3. While `x < y`:
   1. Increase `x` by 1.
   2. If `p < 0`, set `p = p + 2x + 1`. Otherwise decrease `y` by 1 and set `p = p + 2(x - y) + 1`.
   3. Plot the eight symmetric points `(xc ± x, yc ± y)` and `(xc ± y, yc ± x)`.

## Program

`midpoint_circle.py` prints the table of decision parameters `p(k)` and the points of one octant, then opens an
OpenGL window with the pixels drawn as squares on the pixel grid. Each pixel is coloured by the octant it comes
from, which shows the eight-way symmetry, and the ideal circle is drawn over it in black.

## Run

```powershell
pip install PyOpenGL
python midpoint_circle.py
```

Sample input:

```text
xc: 0
yc: 0
r: 10
```

For `r = 10` the decision parameters are -9, -6, -1, 6, -3, 8, 5 and the octant points are
(1, 10), (2, 10), (3, 10), (4, 9), (5, 9), (6, 8), (7, 7). Esc closes the window.

## Result

The Midpoint Circle Drawing Algorithm was implemented in OpenGL using only integer arithmetic, and the full
circle was generated from one octant using eight-way symmetry.
