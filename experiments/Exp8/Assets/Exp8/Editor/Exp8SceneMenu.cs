using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CGVR.Exp8
{
    // Adds the menu item CGVR Lab > Exp 8 - Build Shader Scene. It creates a material that uses the
    // vertex/fragment shader, a few objects that use it, a camera and the ShaderController
    public static class Exp8SceneMenu
    {
        const string RootName = "Exp8 Shader Scene";
        const string ShaderName = "CGVR/Exp8 Vertex Fragment Shader";

        [MenuItem("CGVR Lab/Exp 8 - Build Shader Scene")]
        static void BuildScene()
        {
            Shader shader = Shader.Find(ShaderName);

            if (shader == null)
            {
                Debug.LogError("Shader '" + ShaderName + "' not found. Copy the Assets/Exp8 folder into the project first.");
                return;
            }

            GameObject old = GameObject.Find(RootName);

            if (old != null)
            {
                Object.DestroyImmediate(old);
            }

            DisableTemplateObjects();

            GameObject root = new GameObject(RootName);
            Material material = LoadOrCreateMaterial(shader);

            GameObject sphere = CreateObject(PrimitiveType.Sphere, "Sphere", root.transform, new Vector3(0f, 0f, 0f), 2f, material);
            GameObject left = CreateObject(PrimitiveType.Capsule, "Capsule Left", root.transform, new Vector3(-2.3f, 0f, 0.5f), 0.9f, material);
            GameObject right = CreateObject(PrimitiveType.Capsule, "Capsule Right", root.transform, new Vector3(2.3f, 0f, 0.5f), 0.9f, material);

            GameObject eye = new GameObject("Shader Camera");
            eye.tag = "MainCamera";
            eye.transform.SetParent(root.transform, false);
            eye.transform.position = new Vector3(0f, 0.6f, -5f);
            eye.transform.LookAt(Vector3.zero);

            Camera camera = eye.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.08f, 0.08f, 0.12f);
            camera.fieldOfView = 50f;
            eye.AddComponent<AudioListener>();

            ShaderController controller = root.AddComponent<ShaderController>();
            controller.targets = new Renderer[]
            {
                sphere.GetComponent<Renderer>(),
                left.GetComponent<Renderer>(),
                right.GetComponent<Renderer>(),
            };

            Selection.activeGameObject = root;
            EditorSceneManager.MarkSceneDirty(root.scene);
        }

        static Material LoadOrCreateMaterial(Shader shader)
        {
            // Saved next to the shader so the scene keeps it after it is closed and opened again
            string folder = System.IO.Path.GetDirectoryName(AssetDatabase.GetAssetPath(shader)).Replace('\\', '/');
            string path = folder + "/Exp8 Shader Material.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);

            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
                AssetDatabase.SaveAssets();
            }

            return material;
        }

        static GameObject CreateObject(PrimitiveType type, string name, Transform parent, Vector3 position, float size, Material material)
        {
            GameObject item = GameObject.CreatePrimitive(type);
            item.name = name;
            item.transform.SetParent(parent, false);
            item.transform.localPosition = position;
            item.transform.localScale = Vector3.one * size;
            item.GetComponent<Renderer>().sharedMaterial = material;

            return item;
        }

        static void DisableTemplateObjects()
        {
            // A new Unity scene already has a Main Camera and a Directional Light; this scene brings its own camera
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
