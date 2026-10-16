# Experiment 8: Basic Program using Vertex and Fragment Shaders (Unity)

## Aim

To develop a basic program that renders 3D objects with a hand-written vertex shader and fragment shader, and to
pass values (uniforms) from the application to the shaders every frame, using Unity.

## Course Outcome

Apply the programmable graphics pipeline (vertex and fragment shaders) to render and animate 3D objects.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Describe the stages of the programmable graphics pipeline.
- Write a vertex shader that transforms vertices with the model-view-projection matrix.
- Write a fragment shader that computes the colour of each pixel.
- Pass data from vertices to fragments and see it interpolated by the rasteriser.
- Send uniform values from a C# script to a shader and change them while the program runs.

## Theory

```text
Mesh vertices -> Vertex shader -> Primitive assembly and rasterisation -> Fragment shader -> Screen
```

- The **vertex shader** runs once for every vertex. It must output the vertex position in clip coordinates,
  normally `clip = Projection x View x Model x position` (`UnityObjectToClipPos` in Unity). It can also move the
  vertex and pass extra values, such as a colour or a normal, to the next stage.
- The **rasteriser** finds the pixels covered by each triangle and interpolates the values output by the vertex
  shader across the triangle.
- The **fragment shader** runs once for every covered pixel and returns its final colour.
- **Uniforms** are values that are the same for every vertex and pixel in a draw call (here the animation time,
  the wave amplitude and the colour mode). The C# script sets them with `material.SetFloat` each frame.

Unity shaders are written in HLSL inside a ShaderLab file. Unity compiles them to GLSL when the project uses the
OpenGL graphics API (see the OpenGL note below).

## The shaders

`Assets/Exp8/Shaders/VertexFragmentShader.shader`

- **Vertex shader:** moves every vertex along its normal by a travelling sine wave
  `sin(y * frequency + time * speed) * amplitude`, transforms it to clip space, and gives it a colour that goes
  from red at the bottom to blue at the top.
- **Fragment shader**, mode chosen with keys 1 to 4:

| Key | Mode | Fragment shader operation |
| --- | --- | --- |
| 1 | Interpolated vertex colours | output the colour interpolated from the vertices |
| 2 | Diffuse lighting | colour x (0.25 + 0.75 max(N . L, 0)) |
| 3 | Grayscale | luminance = 0.299 R + 0.587 G + 0.114 B |
| 4 | Normals | colour = N x 0.5 + 0.5 |

`Assets/Exp8/Scripts/ShaderController.cs` sets the uniforms `_Mode`, `_AnimationTime` and `_WaveAmplitude` every
frame, rotates the objects, and shows the current mode, the shader name and the graphics API on screen.

## Setting up in Unity

1. Install Unity Hub and a Unity Editor (2022.3 LTS or Unity 6).
2. Create a new project with the **3D (Built-In Render Pipeline)** or **Universal 3D** template.
3. Copy the folder `Assets/Exp8` from this experiment into the `Assets` folder of the Unity project.
4. Create a new scene (File > New Scene), then choose **CGVR Lab > Exp 8 - Build Shader Scene** from the menu bar.
   This creates a material that uses the shader, a sphere and two capsules that use it, a camera and the controller.
5. Save the scene (File > Save As, for example `Exp8`) and press **Play**.

**To run it on OpenGL:** Edit > Project Settings > Player > Other Settings, untick **Auto Graphics API for
Windows**, add **OpenGLCore** to the list and move it to the top, then restart the editor. The on-screen text then
shows `Graphics API: OpenGLCore`, and the shader runs as GLSL.

## Controls

| Key | Action |
| --- | --- |
| 1 - 4 | Fragment shader mode |
| Up / Down arrow | Increase / decrease the vertex wave amplitude |
| Space | Pause / resume the animation |

## Result

A vertex shader and a fragment shader were written and applied to 3D objects. The vertex shader animated the
geometry and the fragment shader coloured each pixel, with the uniforms controlled from a C# script at run time.
