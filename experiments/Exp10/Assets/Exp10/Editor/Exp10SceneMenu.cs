using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CGVR.Exp10
{
    // Adds the menu item CGVR Lab > Exp 10 - Build Viewing Pipeline Scene. It creates the house, a ground
    // grid, a light, two cameras with side-by-side viewports and the ViewingPipeline script
    public static class Exp10SceneMenu
    {
        const string RootName = "Exp10 Viewing Pipeline Scene";

        [MenuItem("CGVR Lab/Exp 10 - Build Viewing Pipeline Scene")]
        static void BuildScene()
        {
            GameObject old = GameObject.Find(RootName);

            if (old != null)
            {
                Object.DestroyImmediate(old);
            }

            DisableTemplateObjects();

            GameObject root = new GameObject(RootName);
            Material material = DefaultMaterial();

            GameObject sun = new GameObject("Sun");
            sun.transform.SetParent(root.transform, false);
            sun.transform.localRotation = Quaternion.Euler(50f, -30f, 0f);
            Light light = sun.AddComponent<Light>();
            light.type = LightType.Directional;
            light.shadows = LightShadows.Soft;

            CreateGround(root.transform);

            // The modeling transformation of the house: translate, rotate about Y, scale
            GameObject house = new GameObject("House");
            house.transform.SetParent(root.transform, false);
            house.transform.localPosition = new Vector3(0.5f, 0f, 0f);
            house.transform.localRotation = Quaternion.Euler(0f, 30f, 0f);
            CreateHousePart(house.transform, "Walls", false, material, new Color(0.85f, 0.82f, 0.72f));
            CreateHousePart(house.transform, "Roof", true, material, new Color(0.75f, 0.25f, 0.15f));

            ViewingPipeline pipeline = root.AddComponent<ViewingPipeline>();
            pipeline.house = house.transform;
            pipeline.perspectiveCamera = CreateCamera(root.transform, "Perspective Camera", new Rect(0f, 0f, 0.5f, 1f), true);
            pipeline.orthographicCamera = CreateCamera(root.transform, "Orthographic Camera", new Rect(0.5f, 0f, 0.5f, 1f), false);
            pipeline.ApplyCameras();

            Selection.activeGameObject = root;
            EditorSceneManager.MarkSceneDirty(root.scene);
        }

        static Material DefaultMaterial()
        {
            // The default material of a primitive suits whichever render pipeline the project uses
            GameObject temporary = GameObject.CreatePrimitive(PrimitiveType.Cube);
            Material material = temporary.GetComponent<Renderer>().sharedMaterial;
            Object.DestroyImmediate(temporary);
            return material;
        }

        static void CreateHousePart(Transform house, string name, bool roof, Material material, Color color)
        {
            GameObject part = new GameObject(name);
            part.transform.SetParent(house, false);
            part.AddComponent<MeshFilter>();
            part.AddComponent<MeshRenderer>().sharedMaterial = material;

            // Set roof before the mesh is built in OnEnable
            HouseMesh mesh = part.AddComponent<HouseMesh>();
            mesh.roof = roof;
            mesh.enabled = false;
            mesh.enabled = true;

            Tint tint = part.AddComponent<Tint>();
            tint.color = color;
            tint.Apply();
        }

        static void CreateGround(Transform parent)
        {
            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.SetParent(parent, false);
            ground.transform.localScale = new Vector3(0.8f, 1f, 0.8f);
            Tint groundTint = ground.AddComponent<Tint>();
            groundTint.color = new Color(0.82f, 0.84f, 0.88f);
            groundTint.Apply();

            // Grid lines every metre make the perspective (converging) and parallel views easy to compare
            for (int i = -4; i <= 4; i++)
            {
                CreateGridLine(parent, new Vector3(i, 0.005f, 0f), new Vector3(0.03f, 0.01f, 8f));
                CreateGridLine(parent, new Vector3(0f, 0.005f, i), new Vector3(8f, 0.01f, 0.03f));
            }
        }

        static void CreateGridLine(Transform parent, Vector3 position, Vector3 scale)
        {
            GameObject line = GameObject.CreatePrimitive(PrimitiveType.Cube);
            line.name = "Grid Line";
            line.transform.SetParent(parent, false);
            line.transform.localPosition = position;
            line.transform.localScale = scale;
            Object.DestroyImmediate(line.GetComponent<Collider>());
            Tint tint = line.AddComponent<Tint>();
            tint.color = new Color(0.45f, 0.47f, 0.52f);
            tint.Apply();
        }

        static Camera CreateCamera(Transform parent, string name, Rect viewport, bool withListener)
        {
            GameObject eye = new GameObject(name);
            eye.transform.SetParent(parent, false);

            if (withListener)
            {
                eye.tag = "MainCamera";
                eye.AddComponent<AudioListener>();
            }

            Camera camera = eye.AddComponent<Camera>();
            camera.rect = viewport;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = withListener ? new Color(0.16f, 0.2f, 0.28f) : new Color(0.2f, 0.17f, 0.26f);
            return camera;
        }

        static void DisableTemplateObjects()
        {
            // A new Unity scene already has a Main Camera and a Directional Light; this scene brings its own
            Camera templateCamera = Camera.main;

            if (templateCamera != null)
            {
                templateCamera.gameObject.SetActive(false);
            }

            GameObject templateLight = GameObject.Find("Directional Light");

            if (templateLight != null)
            {
                templateLight.SetActive(false);
            }
        }
    }
}
