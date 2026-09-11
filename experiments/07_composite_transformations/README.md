# Experiment 7: Composite Transformations using Matrix Representation

A sequence of 2D transformations is entered one after another, each built as a 3x3 homogeneous matrix.
The matrices are multiplied into a single composite matrix `C = Mn x ... x M2 x M1`, so the whole
sequence is applied to the shape in one matrix multiplication.

The program prints every individual matrix, the composite matrix, the shape after each stage, and the
final points obtained from the composite matrix. The graph shows the original shape (blue dashed), the
intermediate stages (S1, S2 ... in different colours), and the final shape (red solid).

Available transformations: translation, rotation about any pivot, scaling about any fixed point,
reflection, and shearing.

Run:

```powershell
python composite_transformations.py
```

Sample input: a triangle `(1, 1), (4, 1), (1, 3)` scaled by `(2, 2)` about the origin, then rotated
`90` degrees about the origin, then translated by `(5, 0)`.
