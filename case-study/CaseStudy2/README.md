# Case Study 2: Industrial Design and Architecture

**CS4104 CG & VR Assignment – Case Study**

**Scenario:** An automotive manufacturer uses a VR collaborative environment so that design teams in Bengaluru
and Detroit can view and manipulate 1:1 scale car prototypes at the same time, without building expensive
physical clay models.

**Interactive demo (Unity, works on a phone or a laptop browser):** <https://pranav-nayak-123.github.io/CGVR/>
— every answer below can be tried live (see [Interactive demo](#interactive-demo-unity)).

---

## 1. Geometric Modeling: from 2D CAD drawings to 3D meshes

Designers start with 2D information: orthographic views (top, front and side elevations) and sketch profiles made
of lines, arcs and spline curves. The CAD system turns these into a **solid model**, and the solid model is turned
into a **triangle mesh** that both VR sites can render.

### Step 1: 2D profiles to 3D shape (sweep operations)

| Operation | What it does | Car example |
| --- | --- | --- |
| Extrusion (linear sweep) | Moves a 2D profile along a straight line | Door panel thickness, brackets |
| Revolution (rotational sweep) | Rotates a 2D profile about an axis | Wheel rim, tyre, headlamp housing |
| Loft | Blends a series of cross-section profiles | Bonnet and roof surfaces |
| Sweep along a path | Moves a profile along a 3D curve | Window seals, exhaust pipe |

When only orthographic drawings exist, the 3D wireframe is reconstructed from them: points that match across the
top, front and side views give candidate 3D vertices, matching lines give the edges, and closed edge loops give
the faces of the solid.

### Step 2: Representing the solid

**Constructive Solid Geometry (CSG)** builds the object from primitives (box, cylinder, sphere, cone) combined
with regularised Boolean operations: union ∪\*, intersection ∩\* and difference −\*. It is stored as a binary
tree whose leaves are primitives and whose internal nodes are Boolean operations.

```text
Wheel rim = Revolve(rim profile) ∪* Revolve(hub profile) ∪* 5 spokes −* 5 bolt-hole cylinders
```

**Boundary Representation (B-rep)** stores the surface that encloses the solid:

- **Geometry:** faces are NURBS surface patches, edges are curves, vertices are points.
- **Topology:** which faces, edges and vertices connect, stored in a winged-edge or half-edge data structure.

A valid closed solid satisfies Euler's formula: `V − E + F = 2` for a simple solid (a box: 8 − 12 + 6 = 2),
and `V − E + F − H = 2(S − G)` in general (H = holes in faces, S = shells, G = genus / through-holes).

| | CSG | B-rep |
| --- | --- | --- |
| Stores | How the object was built (primitives + Booleans) | The final boundary surfaces |
| Strengths | Compact, easy to edit, always a valid solid | Free-form NURBS "Class-A" body surfaces, fast to display |
| Weaknesses | Hard to model free-form body panels; must be evaluated before display | Larger; topology must be kept consistent |

Industrial CAD kernels (Parasolid, ACIS, Open CASCADE) are **hybrid**: features are built with sweeps and
CSG-style Booleans, and the result is stored as a NURBS B-rep. That is the right fit here: engineers edit the
feature/CSG history, while the VR session only needs the evaluated B-rep surfaces.

### Step 3: B-rep to a VR-ready mesh (tessellation)

1. Each NURBS face is tessellated into triangles with a **chordal (sag) tolerance** – the largest allowed gap
   between a flat triangle and the true curved surface, `e = R(1 − cos(π / N))` for a circle of radius R cut into
   N segments – and an **angle tolerance** between neighbouring normals. Designers judge body surfaces by their
   reflection highlights, so Class-A panels need a fine tolerance (about 0.05–0.1 mm, 10–15°); hidden parts can be
   much coarser.
2. Normals and texture coordinates are generated for the car-paint shaders.
3. **Levels of detail (LODs)** are produced by mesh decimation (for example quadric error metrics): millions of
   triangles for close inspection down to a few thousand for parts seen from far away.
4. The mesh is exported once, centrally, to a real-time format (glTF/FBX), keeping real units (mm → m) so both
   sites see the prototype at exactly **1:1 scale** and with **identical geometry**. Only transforms change
   during the session, so the heavy meshes are sent once, not every frame.

---

## 2. Matrix Transformations: composite matrix for the wheel rim

**Assumptions:** 3D homogeneous coordinates with column vectors, `P' = M · P`. The car faces +x, y is up and the
wheel axle runs along z, so "rotate the rim by 45°" is a rotation about z (the axle) and "move it forward by
50 mm" is a translation of +50 mm along x. The rim's local origin is its hub centre, so scaling and rotation
happen about the hub.

**Order:** scale, then rotate, then translate. The operation applied first is written on the right:

```text
M = T(50, 0, 0) · Rz(45°) · S(1.5, 1.5, 1.5)
```

**Individual matrices** (cos 45° = sin 45° = √2/2 ≈ 0.7071):

```text
S(1.5) =                 Rz(45°) =                       T(50, 0, 0) =
| 1.5  0    0    0 |     | 0.7071  -0.7071  0  0 |       | 1  0  0  50 |
| 0    1.5  0    0 |     | 0.7071   0.7071  0  0 |       | 0  1  0   0 |
| 0    0    1.5  0 |     | 0        0       1  0 |       | 0  0  1   0 |
| 0    0    0    1 |     | 0        0       0  1 |       | 0  0  0   1 |
```

**Composite matrix** (1.5 × 0.7071 = 3√2/4 ≈ 1.0607):

```text
M = T · R · S =
| 1.0607  -1.0607   0     50 |
| 1.0607   1.0607   0      0 |
| 0        0        1.5    0 |
| 0        0        0      1 |
```

**Check with a point** on the rim's edge, P = (100, 0, 0) mm:

```text
M · [100, 0, 0, 1]ᵀ = [1.0607·100 + 50,  1.0607·100,  0,  1]ᵀ = (156.07, 106.07, 0) mm
```

Step by step gives the same result: scaling → (150, 0, 0), rotating 45° → (106.07, 106.07, 0),
translating 50 mm → (156.07, 106.07, 0).

**Why the order matters:** if the translation were applied first (`M' = R · S · T`), the 50 mm move would itself
be scaled and rotated, and the rim would move by (53.03, 53.03, 0) mm – 75 mm diagonally instead of 50 mm
forward. Uniform scaling and rotation about the same point commute, but the translation must be applied last.

**Hub not at the origin:** for a hub at C = (cx, cy, cz), scale and rotate about the hub, then move it:

```text
M = T(cx + 50, cy, cz) · Rz(45°) · S(1.5) · T(−cx, −cy, −cz)
```

**In the shared VR session:** when the Bengaluru designer makes this change, only the 4 × 4 model matrix
(16 floats = 64 bytes) is sent to Detroit, not the mesh. Each headset then draws the rim with
`Projection_eye · View_eye · M` for each of its two eyes, so both teams see the same change within one network
round trip.

---

## 3. Optimisation and Clipping for the headset's dual displays

A VR headset must render **two views (one per eye) at 90 Hz**, which leaves **11.1 ms per frame** for both eyes,
and keep motion-to-photon latency under about 20 ms; dropped frames cause cybersickness. A typical PC headset
has about 2000 × 2000 pixels per eye, so every frame shades around 8 million pixels, and a full engineering car
model can have tens of millions of triangles. Geometry is therefore removed in stages, from the cheapest test to
the most precise.

### Stage 1: Culling – reject whole parts or triangles early

- **View-frustum culling:** each part (door, wheel, seat) has a bounding box in a bounding volume hierarchy
  (BVH). Parts whose box is fully outside the six frustum planes are skipped. For stereo, one combined frustum
  enclosing both eyes is tested, so culling runs once, not twice.
- **Back-face culling:** a triangle facing away from the viewer (`N · V ≤ 0`) cannot be seen on a closed
  surface, which removes about half of each closed part's triangles before rasterisation.
- **Occlusion culling:** parts hidden behind others – the engine behind the closed bonnet, the seats behind the
  closed doors – are skipped using a hierarchical Z-buffer or GPU occlusion queries.
- **Level of detail and foveated rendering:** distant parts use coarser LOD meshes; with eye tracking, full
  resolution is used only where the designer is looking (variable-rate shading).

### Stage 2: Polygon clipping

- **Sutherland–Hodgman polygon clipping** against the view frustum. The frustum is convex and the algorithm
  clips a polygon against one plane at a time – in homogeneous clip space, the six planes −w ≤ x, y, z ≤ w.
  Clipping before the perspective division also removes geometry behind the viewer correctly. This is what the
  GPU's clipping stage implements.
- **The near plane matters especially here:** designers put their heads inside the 1:1 car to inspect the
  cabin, so polygons constantly cross the near plane and must be clipped correctly.
- **Weiler–Atherton clipping** for concave clip regions, such as section/cut-away views that slice the body to
  inspect the inner structure.
- **Cohen–Sutherland or Liang–Barsky line clipping** for CAD edge overlays, dimension lines and measuring tools.

### Stage 3: Hidden surface removal

| Algorithm | Space | Suitability for the VR car model |
| --- | --- | --- |
| **Z-buffer (depth buffer)** | Image | **Main choice.** In GPU hardware, per pixel, any number of polygons in any order, handles intersecting parts, separate per eye |
| **Depth pre-pass (early-Z)** | Image | **Recommended with the Z-buffer:** draw depth first, then run the expensive car-paint/reflection shaders only on visible pixels |
| Sorted transparency / order-independent transparency (A-buffer, weighted blending) | Object / image | **Needed for glass** (windscreen, lamp lenses, glass roof), which the Z-buffer alone cannot blend |
| BSP tree | Object | Good for static scenes but must be rebuilt when parts move – unsuitable for live manipulation |
| Scan-line, Warnock | Image | Historically important; Warnock's subdivision lives on in the hierarchical Z-buffer used for occlusion culling |
| Back-face culling | Object | Not complete alone, but a cheap first step before the Z-buffer |

**Depth precision:** at 1:1 scale with a near plane of about 1 cm (so the head can be inside the car), a standard
depth buffer suffers z-fighting on nearly coplanar body panels and trim. A **32-bit floating-point depth buffer
with reversed-Z** (near → 1, far → 0) spreads precision evenly and avoids it.

**Stereo-specific optimisations:** single-pass instanced stereo (one draw call renders both eyes, so culling and
vertex work are paid once), lens-matched / fixed-foveated shading at the lens edges, and asynchronous
reprojection to keep head tracking smooth if a frame is late.

### Recommended pipeline

```text
BVH frustum culling (shared stereo frustum) → back-face culling → hierarchical-Z occlusion culling → LOD selection
  → Sutherland–Hodgman clipping in homogeneous clip space (both eyes)
  → depth pre-pass + Z-buffer (reversed-Z float depth) for opaque parts
  → sorted / order-independent transparency for glass → per-eye display at 90 Hz
```

---

## Interactive demo (Unity)

The Unity app in [`Assets/CaseStudy2`](Assets/CaseStudy2) turns each answer into something you can try. It runs in
a phone browser (touch) or on a laptop (mouse). Use the phone in **landscape**.

| Tab | What you can do | Answer |
| --- | --- | --- |
| **Modelling** | The car is a CSG union of boxes; tyres and rims are 2D profiles revolved around the axle. Drag the *Rim segments* slider to see triangles vs chordal error `R(1 − cos(π/N))`. | 1 |
| **Transform** | Tap the case-study preset to animate S(1.5) → Rz(45°) → T(50 mm). Or build your own sequence with sliders and +Scale / +Rotate / +Move / +Reflect / +Shear, reorder, undo, animate. The 4 × 4 composite matrix, the check point and a comparison with Unity's own matrices update live; a pink ghost rim shows the wrong order. | 2 |
| **Optimise** | Stereo split screen (two eyes 64 mm apart = the two displays), back-face culling, wheel LOD, live counts of parts/triangles after frustum and back-face culling, frame time against the 11.1 ms budget, and a near-plane slider while sitting inside the cabin. | 3 |
| **Cutaway** | A clipping plane slices the car open; the inside surfaces it exposes are shown in red. | 3 |
| Any tab | **Tap any part** (rim, door, bonnet, mirror, seat) to select it, then drag to move, pinch to scale and twist with two fingers to rotate; its model matrix is shown live. Markers show the Bengaluru and Detroit designers. | 1–3 |

### Running it

1. Copy `Assets/CaseStudy2` into a Unity 6 project (3D Built-In or Universal 3D template).
2. **File → New Scene**, then **CGVR Lab → Case Study 2 - Build Car Design Scene**, save, press **Play**.
3. To publish for phones: add **Web Build Support** to the Unity version in Unity Hub, then
   **CGVR Lab → Case Study 2 - Build for Web (GitHub Pages)** and choose the repo's `docs` folder. GitHub Pages
   serves it at <https://pranav-nayak-123.github.io/CGVR/>.
