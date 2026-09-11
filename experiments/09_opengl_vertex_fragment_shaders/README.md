# Experiment 9: OpenGL Vertex and Fragment Shaders

A modern (core profile 3.3) OpenGL program that renders a rotating RGB triangle using programmable shaders.
The triangle's vertex positions and colours are stored in a vertex buffer (VBO), described by a vertex array
object (VAO), and processed on the GPU by two GLSL shaders.

- The **vertex shader** runs once per vertex. It multiplies each position by a `uniform mat4 transform`
  (a rotation combined with an aspect-ratio correction, built on the CPU with the same homogeneous matrices
  as experiments 6 and 7) and passes the vertex colour on to the next stage.
- The **fragment shader** runs once per pixel inside the triangle. It receives the colour interpolated
  across the triangle by the rasteriser and uses the `mode` and `time` uniforms to compute the final colour.

Pipeline: vertex data (VBO/VAO) → vertex shader → primitive assembly and rasterisation → fragment shader → screen.

## Colour modes

| Key | Mode | Fragment shader operation |
| --- | --- | --- |
| `1` | RGB interpolation | output the interpolated vertex colour |
| `2` | Pulsing brightness | colour × (0.6 + 0.4 sin 3t) |
| `3` | Grayscale | luminance = 0.299 R + 0.587 G + 0.114 B |
| `4` | Inverted colours | 1 − colour |

`Space` pauses or resumes the animation and `Esc` closes the window. The OpenGL version, GLSL version,
and GPU renderer are printed to the console when the program starts.

## Install

```powershell
pip install PyOpenGL glfw
```

## Run

```powershell
python vertex_fragment_shaders.py
```
