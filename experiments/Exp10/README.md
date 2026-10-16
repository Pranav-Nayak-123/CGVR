# Experiment 10: 3D Viewing Pipeline with Projection and Viewport Mapping (Unity)

## Aim

To implement the 3D viewing pipeline (modeling, viewing, projection, clipping, perspective division and viewport
transformations) with 4 x 4 homogeneous matrices for displaying 3D objects on a 2D screen, and to verify it
against the cameras of Unity.

## Course Outcome

Apply 3D viewing transformations and projections to display three-dimensional objects on a two-dimensional device.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- List the coordinate systems a vertex passes through in the 3D viewing pipeline.
- Build the viewing (look-at) matrix from the camera position, look-at point and up vector.
- Build perspective and orthographic projection matrices and compare the two projections.
- Perform the clipping test and perspective division to get normalized device coordinates.
- Map normalized device coordinates to a screen viewport using the viewport transformation.

## Theory

```text
Modeling coords --M--> World coords --V--> Camera coords --P--> Clip coords
    --clipping, divide by w--> Normalized device coords (NDC) --viewport--> Screen coords
```

| Stage | Matrix | What it does |
| --- | --- | --- |
| Modeling | `M = T x Ry x S` | Places the house (defined in its own coordinates) in the world |
| Viewing | `V` (look-at) | Moves the camera to the origin, looking along -z with +y up |
| Projection | `P` | Perspective or orthographic projection into homogeneous clip coordinates |
| Clipping | — | Keeps only points with `-w <= x, y, z <= w` |
| Perspective division | — | `NDC = (x / w, y / w, z / w)`, each in the range [-1, 1] |
| Viewport | — | Maps NDC to the pixel rectangle of the viewport on the screen |

**Viewing matrix.** With camera position `eye`, look-at point `at` and up vector `up`, and
`forward = (at - eye) / |at - eye|`:

```text
u = (up x forward) / |up x forward|      v = forward x u      n = -forward

V = | ux  uy  uz  -u.eye |
    | vx  vy  vz  -v.eye |
    | nx  ny  nz  -n.eye |
    | 0   0   0     1    |
```

(Unity's world is left-handed, so `u = up x forward`. The camera space is the same as OpenGL's: the camera looks
along -z.)

**Perspective projection** (field of view `fov`, aspect ratio `a`, near `n`, far `f`, with `t = 1 / tan(fov / 2)`):

```text
P = | t/a  0       0               0       |
    |  0   t       0               0       |
    |  0   0  (f + n)/(n - f)  2fn/(n - f) |
    |  0   0      -1               0       |
```

Here `w = -z` (the distance in front of the camera), so dividing by `w` makes far objects smaller.

**Orthographic projection** (view volume half width `r` and half height `t`):

```text
P = | 1/r   0      0              0          |
    |  0   1/t     0              0          |
    |  0    0   -2/(f - n)  -(f + n)/(f - n) |
    |  0    0      0              1          |
```

Here `w` stays 1, so parallel lines stay parallel and the size does not change with distance.

**Viewport transformation** for a viewport at `(x, y)` with width `W` and height `H` (Unity screen coordinates
start at the bottom left):

```text
xs = x + (xn + 1) W / 2          ys = y + (yn + 1) H / 2
```

## Algorithm

1. Build `M` from the house's position, rotation about Y and scale.
2. Build `V` from the camera position, the look-at point and the up vector.
3. Build `P` for the perspective camera and for the orthographic camera.
4. For each vertex of the house: `clip = P x V x M x vertex`. Keep it if `-w <= x, y, z <= w`.
5. Divide by `w` to get NDC, then apply the viewport transformation of that camera's viewport.
6. Compare `V`, `P` and the screen points with Unity's `worldToCameraMatrix`, `projectionMatrix` and
   `WorldToScreenPoint`.

## Program

The scene has a house on a ground grid, seen by two cameras placed at the same position: the left half of the
screen is the **perspective** viewport and the right half is the **orthographic** viewport (`Camera.rect`). The
grid lines converge in the perspective view and stay parallel in the orthographic view.

`Assets/Exp10/Scripts/ViewingPipeline.cs` builds every matrix by hand, takes each house vertex through the
pipeline and draws a red square where it lands on the screen; the yellow square is vertex 8 (the front roof peak).
The squares sit exactly on the corners of the house that Unity renders. The text at the bottom shows vertex 8 in
clip coordinates, NDC and screen coordinates, and the largest difference between the hand-made results and
Unity's (close to 0). Press **M** to print all the matrices and the full trace of vertex 8 to the Console.

## Setting up in Unity

1. Install Unity Hub and a Unity Editor (2022.3 LTS or Unity 6).
2. Create a new project with the **3D (Built-In Render Pipeline)** or **Universal 3D** template.
3. Copy the folder `Assets/Exp10` from this experiment into the `Assets` folder of the Unity project.
4. Create a new scene (File > New Scene), then choose **CGVR Lab > Exp 10 - Build Viewing Pipeline Scene** from
   the menu bar.
5. Save the scene (File > Save As, for example `Exp10`) and press **Play**.

## Controls

| Key | Action |
| --- | --- |
| Arrow keys | Orbit the camera around the house |
| + / - | Move the camera closer / farther |
| M | Print the matrices and the trace of vertex 8 to the Console |

## Result

The 3D viewing pipeline was implemented with 4 x 4 homogeneous matrices. The house was taken from modeling
coordinates to screen coordinates for a perspective and an orthographic camera in two viewports, and the
hand-computed matrices and screen positions matched those of Unity's cameras.
