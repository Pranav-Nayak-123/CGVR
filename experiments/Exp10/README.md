# Experiment 10: 3D Viewing Pipeline with Projection and Viewport Mapping

Lab manual: **Experiment 10**. Implement the 3D viewing pipeline, including projection and viewport mapping,
for displaying 3D objects on a 2D screen.

## Aim

To implement the 3D viewing pipeline (modeling, viewing, projection, clipping, perspective division and
viewport transformations) using 4 x 4 homogeneous matrices, and display a 3D object on a 2D screen.

## Course Outcome

Apply 3D viewing transformations and projections to display three-dimensional objects on a two-dimensional device.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- List the coordinate systems a vertex passes through in the 3D viewing pipeline.
- Build the viewing (look-at) matrix from the camera position, look-at point and up vector.
- Build perspective and orthographic projection matrices and compare the two projections.
- Clip lines in homogeneous coordinates and perform perspective division to get normalized device coordinates.
- Map normalized device coordinates to a screen viewport using the viewport transformation.

## Theory

```text
Modeling coords --M--> World coords --V--> Camera coords --P--> Clip coords
    --clipping, divide by w--> Normalized device coords (NDC) --viewport--> Screen coords
```

| Stage | Matrix | What it does |
| --- | --- | --- |
| Modeling | `M = Ry(30) x T(-1, 0, -1)` | Places the object (defined in its own coordinates) in the world |
| Viewing | `V` (look-at) | Moves the camera to the origin, looking along -z with +y up |
| Projection | `P` | Perspective or orthographic projection into homogeneous clip coordinates |
| Clipping | — | Keeps only the parts of lines with `-w <= x, y, z <= w` |
| Perspective division | — | `NDC = (x / w, y / w, z / w)`, each in the range [-1, 1] |
| Viewport | `W` | Maps NDC to the pixel rectangle of the viewport on the screen |

**Viewing matrix.** With camera position `eye`, look-at point `at` and up vector `up`:

```text
n = (eye - at) / |eye - at|      u = (up x n) / |up x n|      v = n x u

V = | ux  uy  uz  -u.eye |
    | vx  vy  vz  -v.eye |
    | nx  ny  nz  -n.eye |
    | 0   0   0     1    |
```

**Perspective projection** (field of view `fov`, aspect ratio `a`, near `n`, far `f`, with `t = 1 / tan(fov / 2)`):

```text
P = | t/a  0       0              0       |
    |  0   t       0              0       |
    |  0   0  (f + n)/(n - f)  2fn/(n - f) |
    |  0   0      -1              0       |
```

Here `w = -z` (the distance in front of the camera), so dividing by `w` makes far objects smaller.

**Orthographic projection** (view volume half width `r` and half height `t`):

```text
P = | 1/r   0      0            0         |
    |  0   1/t     0            0         |
    |  0    0   -2/(f - n)  -(f + n)/(f - n) |
    |  0    0      0            1         |
```

Here `w` stays 1, so parallel lines stay parallel and the size does not change with distance.

**Viewport transformation** for a viewport at `(x, y)` with width `W` and height `H` (screen y grows downwards):

```text
xs = x + (xn + 1) W / 2          ys = y + (1 - yn) H / 2
```

## Algorithm

1. Read the camera position, look-at point, field of view, and near and far distances.
2. Build `M`, `V`, `P` (perspective and orthographic) and the viewport matrix `W` for each viewport.
3. For every edge of the object (and of the ground grid):
   1. Transform both end points to clip coordinates: `clip = P x V x M x point`.
   2. Clip the edge against `-w <= x, y, z <= w` (parametric line clipping).
   3. Divide the clipped end points by `w` to get NDC.
   4. Apply the viewport transformation to get screen coordinates and draw the line.
4. Print every matrix and the coordinates of one vertex at every stage of the pipeline.

## Program

The object is a wireframe house (14 vertices, 20 edges) standing on a ground grid. The same scene is drawn in two
viewports: perspective projection on the left and orthographic (parallel) projection on the right. The grid lines
converge in the perspective view and stay parallel in the orthographic view. Lines that leave the view volume are
clipped at the viewport border.

The console prints `M`, `V` (with the u, v, n camera axes), both projection matrices, both viewport matrices, the
composite matrix `P x V x M`, the coordinates of vertex 8 (the front roof peak, marked with a red dot) at every
stage, and the world and screen coordinates of every vertex.

## Run

```powershell
python viewing_pipeline_3d.py
```

Press Enter to use the default values or type your own:

```text
Camera position (eye) x y z [5 2.5 1.5]:
Look-at point x y z [0 1 0]:
Field of view in degrees [60]:
Near plane distance [1]:
Far plane distance [20]:
```

In the window, the arrow keys orbit the camera around the look-at point and `+` / `-` move it closer or farther.
Moving very close shows the near plane and the viewport edges clipping the house.
Only Python's built-in `tkinter` library is used.

## Result

The 3D viewing pipeline was implemented with homogeneous matrices. The house was transformed from modeling
coordinates to screen coordinates, clipped to the view volume, and displayed in two viewports using perspective
and orthographic projection.
