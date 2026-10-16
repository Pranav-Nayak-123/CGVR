# Experiment 5: Cohen-Sutherland Line Clipping Algorithm

## Aim

To implement the Cohen-Sutherland line clipping algorithm, which uses region codes to clip a line against a
rectangular clipping window, and to display the result using OpenGL.

## Course Outcome

Apply two-dimensional viewing and clipping algorithms to display only the part of a scene inside a window.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Explain the need for clipping in two-dimensional viewing.
- Assign 4-bit region codes (outcodes) to the end points of a line.
- Use the region codes to accept or reject lines without computing intersections.
- Compute the intersection of a line with the edges of the clipping window.
- Implement the Cohen-Sutherland algorithm in OpenGL.

## Theory

The edges of the clipping window `(xmin, ymin)` to `(xmax, ymax)`, extended across the plane, divide it into nine
regions. Each region has a 4-bit code, with the bits in the order TOP BOTTOM RIGHT LEFT:

```text
1001 | 1000 | 1010
-----+------+-----
0001 | 0000 | 0010
-----+------+-----
0101 | 0100 | 0110
```

- If both end points have code `0000`, the line is completely inside: **trivially accepted**.
- If `code1 AND code2` is not `0000`, both points are on the outside of the same edge: **trivially rejected**.
- Otherwise the line is cut at one window edge, the outside end point is replaced by the intersection point,
  and the test is repeated.

Intersections with a vertical edge `x = xe` and a horizontal edge `y = ye`:

```text
y = y1 + (y2 - y1)(xe - x1) / (x2 - x1)          x = x1 + (x2 - x1)(ye - y1) / (y2 - y1)
```

## Algorithm

1. Read the clipping window and the two end points of the line.
2. Compute the region codes `code1` and `code2` of the end points.
3. If both codes are `0000`, accept the line and stop.
4. If `code1 AND code2` is not `0000`, reject the line and stop.
5. Pick an end point that is outside. Using its code, find where the line crosses the top, bottom, right or
   left edge, replace that end point with the intersection, recompute its code and go back to step 3.

## Program

`cohen_sutherland_line_clipping.py` prints every step of the algorithm (codes, the edge used and the intersection
point) and the final clipped line. The OpenGL window shows the nine regions with their codes, the clipping
window, the original line (red, dashed) and the clipped line (blue).

## Run

```powershell
pip install PyOpenGL
python cohen_sutherland_line_clipping.py
```

Sample input:

```text
Enter bottom-left corner (x y): 2 2
Enter top-right corner (x y): 8 6
Enter first endpoint (x y): 0 1
Enter second endpoint (x y): 10 7
```

The clipped line is `(2.00, 2.20)` to `(8.00, 5.80)`. Esc closes the window.

## Result

The Cohen-Sutherland line clipping algorithm was implemented in OpenGL, and the part of the line inside the
clipping window was found using region codes and edge intersections.
