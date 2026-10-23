# CGVR

Computer Graphics and Virtual Reality lab records.

## Experiments

| No. | Experiment | Program | Uses |
| --- | --- | --- | --- |
| 0 | OpenGL bouncing triangle | `experiments/Exp0/main.py` | Python, OpenGL (glfw) |
| 1 | DDA and Bresenham line drawing algorithms | `experiments/Exp1/dda_bresenham.py` | Python, OpenGL |
| 2 | Midpoint circle drawing algorithm | `experiments/Exp2/midpoint_circle.py` | Python, OpenGL |
| 3 | 2D transformations using homogeneous coordinates | `experiments/Exp3/transformations_2d.py` | Python, OpenGL |
| 4 | Composite transformations using matrix representation | `experiments/Exp4/composite_transformations.py` | Python, OpenGL |
| 5 | Cohen-Sutherland line clipping | `experiments/Exp5/cohen_sutherland_line_clipping.py` | Python, OpenGL |
| 6 | Z-buffer algorithm for hidden surface removal | `experiments/Exp6/z_buffer.py` | Python, OpenGL |
| 7 | Phong illumination model for a 3D object | `experiments/Exp7/phong_illumination.py` | Python, OpenGL |
| 8 | Basic program using vertex and fragment shaders | `experiments/Exp8/Assets/Exp8` | Unity |
| 9 | Simple interactive 3D scene | `experiments/Exp9/Assets/Exp9` | Unity |
| 10 | 3D viewing pipeline with projection and viewport mapping | `experiments/Exp10/Assets/Exp10` | Unity |

Each experiment folder has a README with the aim, course outcome, learning objectives, theory, algorithm,
how to run it and the result.

## Case studies

| Case study | Write-up | Interactive demo |
| --- | --- | --- |
| 2. Industrial Design and Architecture (VR car design, Bengaluru + Detroit) | [`case-study/CaseStudy2`](case-study/CaseStudy2) | Unity, runs on a phone or laptop browser: <https://pranav-nayak-123.github.io/CGVR/> |

## Running the OpenGL experiments (0 to 7)

```powershell
pip install PyOpenGL glfw
cd experiments/Exp1
python dda_bresenham.py
```

`glfw` is only needed for experiment 0. On Windows, `pip install PyOpenGL` also installs GLUT (freeglut),
which experiments 1 to 7 use for their windows and text.

## Running the Unity experiments (8 to 10)

1. Install Unity Hub and a Unity Editor (2022.3 LTS or Unity 6).
2. Create a new project with the **3D (Built-In Render Pipeline)** or **Universal 3D** template.
3. Copy `experiments/ExpN/Assets/ExpN` into the project's `Assets` folder. All three can go into the same project.
4. Create a new scene (File > New Scene) and choose **CGVR Lab > Exp N - Build ... Scene** from the menu bar.
5. Save the scene and press **Play**.

Screenshots of the outputs are in the `output` folder.
