# Experiment 9: Phong Illumination Model

Lab manual: **Experiment 7**. Implement the Phong illumination model for a 3D object.

## Aim

To implement the Phong illumination model, combining ambient, diffuse and specular reflection, to compute the
intensity of light reflected from every point on the surface of a 3D object (a sphere).

## Course Outcome

Apply illumination models to compute the shading of 3D objects.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Explain the ambient, diffuse and specular components of reflected light.
- Compute the unit vectors N, L, V and R at a point on a surface.
- Apply Lambert's cosine law for diffuse reflection.
- Explain how the shininess exponent n controls the size of the specular highlight.
- Implement the Phong illumination model and observe the effect of ka, kd, ks, n and the light position.

## Theory

The Phong illumination model gives the intensity at a surface point as the sum of three terms:

```text
I = ka Ia  +  kd Il max(N . L, 0)  +  ks Il max(R . V, 0)^n
    ambient   diffuse                 specular
```

| Symbol | Meaning |
| --- | --- |
| `Ia`, `Il` | Intensity of the ambient light and of the point light source |
| `ka`, `kd`, `ks` | Ambient, diffuse and specular reflection coefficients (0 to 1) |
| `n` | Shininess (specular exponent). A larger n gives a smaller, sharper highlight |
| `N` | Unit surface normal at the point |
| `L` | Unit vector from the point towards the light |
| `V` | Unit vector from the point towards the viewer |
| `R` | Reflection of L about N: `R = 2 (N . L) N - L` |

- **Ambient** light is scattered evenly by the surroundings, so it lights every point equally.
- **Diffuse** reflection follows Lambert's cosine law. It is brightest where the surface faces the light and zero
  where `N . L <= 0` (the side facing away from the light).
- **Specular** reflection is the shiny highlight seen when the reflected ray R points towards the viewer.

For colour, the ambient and diffuse terms are multiplied by the object colour `Od`, and the specular term by the
light colour `Os` (white), so the highlight looks white:

```text
I = (ka Ia + kd Il max(N . L, 0)) Od + ks Il max(R . V, 0)^n Os
```

## Algorithm

1. Read the light position and the coefficients `ka`, `kd`, `ks` and `n`.
2. For each pixel `(x, y)` of the image, check whether the ray along the z axis hits the sphere: `x² + y² <= r²`.
   If it does not, use the background colour.
3. Find the visible surface point `P = (x, y, sqrt(r² - x² - y²))` and the unit normal `N = P / r`.
4. Compute `L = normalise(light - P)`, `V = normalise(viewer - P)` and `R = 2 (N . L) N - L`.
5. Compute the ambient, diffuse and specular terms. The specular term is zero when `N . L <= 0`.
6. Combine the terms, clamp each RGB channel to `[0, 1]` and set the pixel colour.

## Program

The window shows four images of the same sphere: the ambient term only, the diffuse term only, the specular term
only, and the full Phong model (their sum). The console prints the complete calculation (N, L, V, R, N.L, R.V, the
three terms and the final colour) for three sample points: one near the highlight, one facing the viewer and one
on the side facing away from the light.

## Run

```powershell
python phong_illumination.py
```

Press Enter to use the default values or type your own:

```text
Light position (x y z) [2.5 2.5 4]:
Ambient reflection coefficient ka [0.2]:
Diffuse reflection coefficient kd [0.7]:
Specular reflection coefficient ks [0.6]:
Shininess (specular exponent) n [32]:
```

In the window, the arrow keys move the light and `+` / `-` double or halve the shininess `n`.
Only Python's built-in `tkinter` library is used.

## Result

The Phong illumination model was implemented for a sphere. The ambient, diffuse and specular components were
computed separately and combined, and changing the light position and the shininess moved and resized the
specular highlight as expected.
