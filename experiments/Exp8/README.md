# Experiment 8: Z-Buffer Algorithm for Hidden Surface Removal

Lab manual: **Experiment 6**. Implement the Z-buffer algorithm for hidden surface removal.

## Aim

To implement the Z-buffer (depth buffer) algorithm for hidden surface removal, so that when 3D objects overlap
on the screen only the surface nearest to the viewer is displayed at every pixel.

## Course Outcome

Apply visible surface detection (hidden surface removal) methods to display 3D scenes correctly.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Explain why hidden surface removal is needed when 3D objects are projected onto a 2D screen.
- Describe the frame buffer and the depth (Z) buffer and how each one is initialised.
- Compute the depth of a polygon at a pixel from its plane equation and update it incrementally along a scan line.
- Implement the per-pixel depth test that keeps only the nearest surface.
- Compare the Z-buffer result with drawing the polygons in a fixed order.

## Theory

The Z-buffer method is an image-space method: the visibility decision is made separately for every pixel.
Two buffers of the same size as the screen are used:

- **Frame buffer** `frame(x, y)` stores the colour of each pixel.
- **Depth buffer** `depth(x, y)` stores the depth of the nearest surface found so far at that pixel.

Polygons can be processed in any order. For a polygon lying in the plane `Ax + By + Cz + D = 0`, the depth at a pixel is

```text
z = (-A x - B y - D) / C
```

Moving one pixel to the right along a scan line changes `x` by 1, so the next depth needs only one addition:

```text
z(x + 1) = z(x) - A / C
```

Advantages: simple, works for any polygons in any order, and handles surfaces that pass through each other.
Disadvantages: needs extra memory for the depth buffer, and depth precision is limited.

## Algorithm

1. For every pixel set `depth(x, y) = infinity` (farthest) and `frame(x, y) = background colour`.
2. For each polygon of the scene:
   1. Transform its vertices to screen coordinates `(x, y)` and keep the depth `z` of each vertex.
   2. Find the plane coefficients `A, B, C, D` of the polygon. If `C = 0` the polygon is seen edge-on and is skipped.
   3. Scan-convert the polygon. For each pixel `(x, y)` inside it compute `z` from the plane equation
      (incrementally along each scan line).
   4. If `z < depth(x, y)`, set `depth(x, y) = z` and `frame(x, y) = colour of the polygon`.
3. When all polygons are processed, the frame buffer holds the visible surfaces and the depth buffer holds the
   depth of the nearest surface at each pixel.

## Program

- The scene has a cube, a pyramid and a slanted plate that passes through both solids (12 faces in total).
- The objects are rotated about the Y axis and then the X axis, and projected orthographically onto a
  300 x 300 frame buffer. The viewer looks along -z, so `depth = -z` and a smaller depth is nearer.
- No back-face culling is done. Every face, including the back faces, goes through the depth test, so the
  Z-buffer alone decides what is visible.

The window shows three panels:

| Panel | Meaning |
| --- | --- |
| Without Z-buffer | Faces drawn in list order with no depth test. Back faces and the plate wrongly cover the front faces. |
| With Z-buffer | Correct result. The plate disappears inside the cube and the pyramid and the hidden faces are removed. |
| Depth buffer | Final contents of the depth buffer as grey levels (brighter = nearer, black = nothing drawn). |

The console prints, for every face, the number of pixels tested, written and finally visible, and whether
the face is fully visible, partly hidden or hidden, along with the totals for the whole scene.

## Run

```powershell
python z_buffer.py
```

Press Enter to use the default view or type your own angles:

```text
Rotation about the Y axis in degrees [-20]:
Rotation about the X axis in degrees [20]:
```

In the window, the arrow keys rotate the view and all three panels are drawn again.
Only Python's built-in `tkinter` library is used.

## Result

The Z-buffer algorithm was implemented and the hidden surfaces were removed correctly, including the parts
of the plate that lie inside the cube and the pyramid, which drawing the faces in a fixed order cannot handle.
