# Experiment 4: Composite Transformations using Matrix Representation

## Aim

To implement composite two-dimensional transformations by multiplying the homogeneous matrices of a sequence of
transformations into a single matrix, and to apply that matrix to an object in OpenGL.

## Course Outcome

**CO2:** Apply two-dimensional graphics transformations using matrix representation and homogeneous coordinates
for graphical object manipulation.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Represent each basic transformation as a 3 x 3 homogeneous matrix.
- Combine a sequence of transformations into one composite matrix.
- Explain why the order of matrix multiplication matters.
- Perform rotation and scaling about an arbitrary point as a composite transformation.
- Apply composite transformations with the OpenGL matrix stack.

## Theory

If transformation `M1` is applied first, then `M2`, ..., then `Mn`, the point is transformed as

```text
P' = Mn · ... · M2 · M1 · P = C · P,     where C = Mn · ... · M2 · M1
```

The composite matrix `C` is computed once and then applied to every vertex with a single multiplication.
Matrix multiplication is not commutative, so changing the order of the transformations changes the result.
For example, rotation about a pivot `(px, py)` is the composite `T(px, py) · R(θ) · T(-px, -py)`.

OpenGL builds the same product on its matrix stack: `glMultMatrixf(M)` post-multiplies the current matrix, so
calling it for `Mn` first and `M1` last gives `Mn · ... · M1`.

## Algorithm

1. Read the vertices of the shape.
2. Read the transformations in the order they are to be applied, and build each matrix `M1, M2, ..., Mn`.
3. Compute `C = Mn · ... · M2 · M1`.
4. Apply `C` to every vertex, and also apply the steps one by one to check that the results match.
5. Draw the original shape, the intermediate shapes, and the final shape drawn with OpenGL's matrix stack.

## Program

`composite_transformations.py` supports translation, rotation about any pivot, scaling about any fixed point,
reflection and shearing, in any order and number. It prints every matrix, the composite matrix, the shape after
each stage and the final vertices. In the OpenGL window the original shape is blue and dashed, the intermediate
stages S1, S2, ... are dashed in different colours, and the final red shape is drawn by OpenGL's matrix stack.
The red dots are the vertices computed with the single composite matrix `C`.

## Run

```powershell
pip install PyOpenGL
python composite_transformations.py
```

Sample input: the triangle `(1, 1), (4, 1), (1, 3)` scaled by `(2, 2)` about the origin, then rotated `90`
degrees about the origin, then translated by `(5, 0)`. The composite matrix is

```text
| 0  -2  5 |
| 2   0  0 |
| 0   0  1 |
```

and the final triangle is `(3, 2), (3, 8), (-1, 2)`. Esc closes the window.

## Result

Composite transformations were implemented by multiplying homogeneous matrices into a single matrix, and the
result was verified against applying the transformations one by one and against OpenGL's matrix stack.
