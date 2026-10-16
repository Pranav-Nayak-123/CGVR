# Experiment 3: Implementation of Two-Dimensional Transformations using Homogeneous Coordinates

## Aim

To implement the fundamental two-dimensional geometric transformations using homogeneous coordinate
representation and transformation matrices in OpenGL.

## Course Outcome

**CO2:** Apply two-dimensional graphics transformations using matrix representation and homogeneous coordinates
for graphical object manipulation.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Understand coordinate transformations.
- Apply matrix operations in computer graphics.
- Implement translation, rotation, scaling, reflection and shearing.
- Understand homogeneous coordinates.
- Develop OpenGL programs for geometric transformations.

## Theory

In homogeneous coordinates a point `(x, y)` is written as `[x, y, 1]`, so every 2D transformation, including
translation, becomes a 3 x 3 matrix and is applied as `P' = M · P`.

```text
Translation        Rotation (anticlockwise θ)    Scaling            Shearing
| 1  0  tx |       | cosθ  -sinθ  0 |            | sx  0   0 |      | 1    shx  0 |
| 0  1  ty |       | sinθ   cosθ  0 |            | 0   sy  0 |      | shy  1    0 |
| 0  0  1  |       | 0      0     1 |            | 0   0   1 |      | 0    0    1 |

Reflection about the X axis: diag(1, -1, 1)      about the Y axis: diag(-1, 1, 1)
about the origin: diag(-1, -1, 1)                 about y = x: swap x and y      about y = -x: x' = -y, y' = -x
```

Rotation about a pivot `(px, py)` and scaling about a fixed point use `T(px, py) · M · T(-px, -py)`.

## Algorithm

1. Read the vertices of the shape.
2. Read the transformation and its parameters, and build its 3 x 3 homogeneous matrix `M`.
3. Multiply each vertex `[x, y, 1]` by `M` to get the transformed vertex.
4. Draw the original shape, and draw the shape again after loading `M` into OpenGL with `glMultMatrixf`.

## Program

`transformations_2d.py` supports translation, rotation about any pivot, scaling about any fixed point, reflection
(X axis, Y axis, origin, y = x, y = -x) and shearing. It prints the matrix and the transformed vertices. In the
OpenGL window the original shape is blue and dashed. The red shape is drawn by OpenGL from the original vertices
after `glMultMatrixf(M)`, and the red dots are the vertices computed by the program's own matrix multiplication,
so the two results can be seen to agree.

## Run

```powershell
pip install PyOpenGL
python transformations_2d.py
```

Sample input (shearing a rectangle):

```text
Number of vertices: 4
x1: 0   y1: 0
x2: 4   y2: 0
x3: 4   y3: 3
x4: 0   y4: 3
Choice: 5
Shear along x (shx): 1
Shear along y (shy): 0
```

Esc closes the window.

## Result

Translation, rotation, scaling, reflection and shearing were implemented with 3 x 3 homogeneous matrices in
OpenGL, and the transformed shapes were displayed along with the original.
