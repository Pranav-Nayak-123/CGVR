# Experiment 9: Simple Interactive 3D Scene using Unity

## Aim

To create a simple interactive 3D scene in Unity with objects, materials, lights, a camera, physics and C#
scripts that respond to keyboard and mouse input.

## Course Outcome

Apply a game engine to build interactive 3D and virtual environments.

## Bloom's Taxonomy Level

L3 – Apply

## Learning Objectives

After completing this experiment, the student will be able to

- Create and arrange GameObjects using Unity's primitives and the Transform component (position, rotation, scale).
- Add lights and a camera to a scene and set their properties.
- Write C# scripts (MonoBehaviour) that use `Start`, `Update`, `OnTriggerEnter` and `OnGUI`.
- Handle keyboard and mouse input to move a first-person player and interact with objects.
- Use Unity physics: colliders, triggers, rigidbodies, the CharacterController and raycasting.

## The scene

| Part | What it shows |
| --- | --- |
| Ground and four walls | Primitives (plane and cubes) placed and scaled with Transforms |
| Sun (directional light) | Lighting with soft shadows |
| Lamp (point light) | A second light that can be switched on and off with **L** |
| Spinning cube on a pedestal | A script that rotates an object every frame (`Spinner`) |
| Three colour cubes | Raycasting: click the cube in the centre of the screen to change its colour (`ColorChanger`) |
| Balls and stacked crates | Rigidbody physics: walk into them to push them over |
| Five gold coins | Trigger colliders: walk through them to collect them, the score is shown on screen (`Collectible`) |
| Player | First-person camera with a CharacterController: walk, look around and jump (`PlayerController`) |

All the objects are created from C# by `SceneBuilder`, so the scene can be rebuilt at any time.

## Scripts

`Assets/Exp9/Scripts`

| Script | Purpose |
| --- | --- |
| `SceneBuilder.cs` | Creates all the objects, lights, the camera and the player |
| `PlayerController.cs` | Walking, mouse look, jumping, clicking objects, pushing rigidbodies |
| `LabGame.cs` | Score, on-screen instructions, lamp switch and reset |
| `Collectible.cs` | Coin that is collected when the player enters its trigger |
| `ColorChanger.cs` | Cycles an object through a list of colours |
| `Spinner.cs` | Rotates an object continuously |
| `Tint.cs` | Gives each object its own colour (works with the built-in pipeline and URP) |
| `GameInput.cs` | Reads the keyboard and mouse with either the old Input Manager or the new Input System |

## Setting up in Unity

1. Install Unity Hub and a Unity Editor (2022.3 LTS or Unity 6).
2. Create a new project with the **3D (Built-In Render Pipeline)** or **Universal 3D** template.
3. Copy the folder `Assets/Exp9` from this experiment into the `Assets` folder of the Unity project.
4. Create a new scene (File > New Scene), then choose **CGVR Lab > Exp 9 - Build Interactive Scene** from the
   menu bar. All the objects appear in the Hierarchy and the Scene view.
5. Save the scene (File > Save As, for example `Exp9`) and press **Play**. Click in the Game view to capture the mouse.

## Controls

| Key / mouse | Action |
| --- | --- |
| W A S D / arrow keys | Walk |
| Mouse | Look around |
| Space | Jump |
| Left click | Change the colour of the cube in the centre of the screen |
| L | Lamp on / off |
| R | Reset the scene |
| Esc | Free the mouse cursor |

## Result

A simple interactive 3D scene was created in Unity with primitives, materials, lights, a first-person camera,
physics objects, collectible triggers and C# scripts that respond to keyboard and mouse input.
