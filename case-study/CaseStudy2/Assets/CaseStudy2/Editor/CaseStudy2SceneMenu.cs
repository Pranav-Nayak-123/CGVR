using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CGVR.CaseStudy2
{
    // Menu items:
    //   CGVR Lab > Case Study 2 - Build Car Design Scene : creates the 1:1 car, cameras and the app in the open scene
    //   CGVR Lab > Case Study 2 - Build for Web (GitHub Pages) : builds the open scene for phone and desktop browsers
    public static class CaseStudy2SceneMenu
    {
        const string RootName = "CaseStudy2 Car Design Scene";
        const string ShaderName = "CGVR/CaseStudy2 Clip";

        [MenuItem("CGVR Lab/Case Study 2 - Build Car Design Scene")]
        static void BuildScene()
        {
            Shader shader = Shader.Find(ShaderName);

            if (shader == null)
            {
                Debug.LogError("Shader '" + ShaderName + "' not found. Copy the Assets/CaseStudy2 folder into the project first.");
                return;
            }

            GameObject old = GameObject.Find(RootName);

            if (old != null)
            {
                Object.DestroyImmediate(old);
            }

            DisableTemplateObjects();

            Material material = LoadOrCreateMaterial(shader);
            GameObject root = new GameObject(RootName);
            Transform car = new GameObject("Car").transform;
            car.SetParent(root.transform, false);

            // Car body: a CSG union of boxes. The car faces +X, Y is up and the wheel axles run along Z
            Color paint = new Color(0.12f, 0.32f, 0.72f);
            Part(car, "Body", new Vector3(0f, 0.55f, 0f), Vector3.zero, new Vector3(4.3f, 0.6f, 1.8f), paint, material);
            Part(car, "Cabin", new Vector3(-0.25f, 1.1f, 0f), Vector3.zero, new Vector3(2.1f, 0.55f, 1.6f), paint, material);
            Part(car, "Bonnet", new Vector3(1.45f, 0.88f, 0f), Vector3.zero, new Vector3(1.3f, 0.08f, 1.7f), paint * 1.1f, material);
            Part(car, "Windscreen", new Vector3(0.95f, 1.08f, 0f), new Vector3(0f, 0f, 38f), new Vector3(0.04f, 0.62f, 1.5f), new Color(0.55f, 0.75f, 0.9f), material);
            Part(car, "Door Left", new Vector3(-0.1f, 0.62f, 0.905f), Vector3.zero, new Vector3(1.2f, 0.5f, 0.03f), paint * 0.9f, material);
            Part(car, "Door Right", new Vector3(-0.1f, 0.62f, -0.905f), Vector3.zero, new Vector3(1.2f, 0.5f, 0.03f), paint * 0.9f, material);
            Part(car, "Mirror Left", new Vector3(0.7f, 1.0f, 0.98f), Vector3.zero, new Vector3(0.12f, 0.1f, 0.18f), new Color(0.2f, 0.2f, 0.22f), material);
            Part(car, "Mirror Right", new Vector3(0.7f, 1.0f, -0.98f), Vector3.zero, new Vector3(0.12f, 0.1f, 0.18f), new Color(0.2f, 0.2f, 0.22f), material);
            Part(car, "Headlamp Left", new Vector3(2.16f, 0.66f, 0.6f), Vector3.zero, new Vector3(0.04f, 0.14f, 0.35f), new Color(1f, 0.95f, 0.7f), material);
            Part(car, "Headlamp Right", new Vector3(2.16f, 0.66f, -0.6f), Vector3.zero, new Vector3(0.04f, 0.14f, 0.35f), new Color(1f, 0.95f, 0.7f), material);
            Part(car, "Seat Driver", new Vector3(-0.35f, 0.95f, 0.35f), Vector3.zero, new Vector3(0.5f, 0.5f, 0.45f), new Color(0.35f, 0.3f, 0.28f), material);
            Part(car, "Seat Passenger", new Vector3(-0.35f, 0.95f, -0.35f), Vector3.zero, new Vector3(0.5f, 0.5f, 0.45f), new Color(0.35f, 0.3f, 0.28f), material);
            Part(car, "Dashboard", new Vector3(0.55f, 1.0f, 0f), Vector3.zero, new Vector3(0.3f, 0.2f, 1.5f), new Color(0.15f, 0.15f, 0.17f), material);

            LatheShape ghost;
            LatheShape frontLeft = Wheel(car, "Wheel Front Left", new Vector3(1.35f, 0.33f, 0.85f), false, material, out ghost);
            LatheShape unused;
            LatheShape frontRight = Wheel(car, "Wheel Front Right", new Vector3(1.35f, 0.33f, -0.85f), true, material, out unused);
            LatheShape rearLeft = Wheel(car, "Wheel Rear Left", new Vector3(-1.35f, 0.33f, 0.85f), false, material, out unused);
            LatheShape rearRight = Wheel(car, "Wheel Rear Right", new Vector3(-1.35f, 0.33f, -0.85f), true, material, out unused);

            GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Studio Floor";
            ground.transform.SetParent(root.transform, false);
            ground.transform.localScale = new Vector3(1.6f, 1f, 1.6f);
            ground.GetComponent<Renderer>().sharedMaterial = material;
            AddTint(ground, new Color(0.62f, 0.64f, 0.68f), false);

            Transform bengaluru = Marker(root.transform, "Bengaluru Designer", new Vector3(2.6f, 1.6f, 2.4f), new Color(1f, 0.55f, 0.1f), material);
            Transform detroit = Marker(root.transform, "Detroit Designer", new Vector3(-2.8f, 1.6f, -2.2f), new Color(0.2f, 0.75f, 0.95f), material);

            Transform rig = new GameObject("Camera Rig").transform;
            rig.SetParent(root.transform, false);
            Camera left = CreateEye(rig, "Left Eye", true);
            Camera right = CreateEye(rig, "Right Eye", false);
            right.enabled = false;

            CaseStudyApp app = root.AddComponent<CaseStudyApp>();
            app.leftEye = left;
            app.rightEye = right;
            app.car = car;
            app.studiedRim = frontLeft;
            app.ghostRim = ghost;
            app.rims = new[] { frontLeft, frontRight, rearLeft, rearRight };
            app.carMaterial = material;
            app.bengaluruMarker = bengaluru;
            app.detroitMarker = detroit;

            left.transform.position = new Vector3(4f, 2.8f, 5.7f);
            left.transform.LookAt(new Vector3(0f, 0.7f, 0f));

            Selection.activeGameObject = root;
            EditorSceneManager.MarkSceneDirty(root.scene);
        }

        [MenuItem("CGVR Lab/Case Study 2 - Build for Web (GitHub Pages)")]
        static void BuildForWeb()
        {
            string scene = EditorSceneManager.GetActiveScene().path;

            if (string.IsNullOrEmpty(scene))
            {
                EditorUtility.DisplayDialog("Case Study 2", "Save the scene first (File > Save).", "OK");
                return;
            }

            string folder = EditorUtility.SaveFolderPanel("Choose the 'docs' folder inside your CGVR repository", "", "docs");

            if (string.IsNullOrEmpty(folder))
            {
                return;
            }

            // GitHub Pages cannot send the headers Unity's compressed files need, so let the page
            // decompress them itself (works on every web server, including phone browsers)
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
            PlayerSettings.WebGL.decompressionFallback = true;

            BuildReport report = BuildPipeline.BuildPlayer(new[] { scene }, folder, BuildTarget.WebGL, BuildOptions.None);

            if (report.summary.result == BuildResult.Succeeded)
            {
                EditorUtility.DisplayDialog("Case Study 2", "Web build finished in:\n" + folder, "OK");
            }
            else
            {
                EditorUtility.DisplayDialog("Case Study 2",
                    "The web build failed. If Unity says the Web/WebGL module is missing, add 'Web Build Support' to this " +
                    "Unity version in Unity Hub (Installs > gear icon > Add modules) and try again. See the Console for details.",
                    "OK");
            }
        }

        static GameObject Part(Transform parent, string name, Vector3 position, Vector3 rotation, Vector3 scale, Color color, Material material)
        {
            GameObject part = GameObject.CreatePrimitive(PrimitiveType.Cube);
            part.name = name;
            part.transform.SetParent(parent, false);
            part.transform.localPosition = position;
            part.transform.localRotation = Quaternion.Euler(rotation);
            part.transform.localScale = scale;
            part.GetComponent<Renderer>().sharedMaterial = material;
            AddTint(part, color, true);
            return part;
        }

        // A wheel at the hub position: a tyre and a rim, both revolved profiles. Right-hand wheels are turned
        // 180 degrees so the spokes face outwards. The front-left wheel also gets the hidden ghost rim.
        static LatheShape Wheel(Transform car, string name, Vector3 hub, bool rightSide, Material material, out LatheShape ghost)
        {
            Transform wheel = new GameObject(name).transform;
            wheel.SetParent(car, false);
            wheel.localPosition = hub;
            wheel.localRotation = rightSide ? Quaternion.Euler(0f, 180f, 0f) : Quaternion.identity;

            Lathe(wheel, "Tyre", LatheKind.Tyre, new Color(0.08f, 0.08f, 0.09f), material);
            LatheShape rim = Lathe(wheel, "Rim", LatheKind.Rim, new Color(0.78f, 0.79f, 0.82f), material);
            ghost = null;

            if (name == "Wheel Front Left")
            {
                ghost = Lathe(wheel, "Ghost Rim (wrong order)", LatheKind.Rim, new Color(0.95f, 0.3f, 0.75f), material);
                ghost.gameObject.SetActive(false);
            }

            return rim;
        }

        static LatheShape Lathe(Transform parent, string name, LatheKind kind, Color color, Material material)
        {
            GameObject item = new GameObject(name);
            item.transform.SetParent(parent, false);
            item.AddComponent<MeshFilter>();
            item.AddComponent<MeshRenderer>().sharedMaterial = material;
            item.AddComponent<MeshCollider>();

            // Set the kind before the mesh is built in OnEnable
            LatheShape shape = item.AddComponent<LatheShape>();
            shape.kind = kind;
            shape.enabled = false;
            shape.enabled = true;

            AddTint(item, color, true);
            return shape;
        }

        static Transform Marker(Transform parent, string name, Vector3 position, Color color, Material material)
        {
            GameObject marker = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            marker.name = name;
            marker.transform.SetParent(parent, false);
            marker.transform.localPosition = position;
            marker.transform.localScale = Vector3.one * 0.3f;
            marker.GetComponent<Renderer>().sharedMaterial = material;
            AddTint(marker, color, false);
            return marker.transform;
        }

        static void AddTint(GameObject item, Color color, bool clippable)
        {
            Tint tint = item.AddComponent<Tint>();
            tint.color = color;
            tint.clippable = clippable;
            tint.Apply();
        }

        static Camera CreateEye(Transform rig, string name, bool main)
        {
            GameObject eye = new GameObject(name);
            eye.transform.SetParent(rig, false);

            if (main)
            {
                eye.tag = "MainCamera";
                eye.AddComponent<AudioListener>();
            }

            Camera camera = eye.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.13f, 0.15f, 0.2f);
            camera.fieldOfView = 60f;
            camera.nearClipPlane = 0.05f;
            return camera;
        }

        static Material LoadOrCreateMaterial(Shader shader)
        {
            // Saved next to the shader so the scene (and the web build) keeps it
            string folder = System.IO.Path.GetDirectoryName(AssetDatabase.GetAssetPath(shader)).Replace('\\', '/');
            string path = folder + "/CaseStudy2 Material.mat";
            Material material = AssetDatabase.LoadAssetAtPath<Material>(path);

            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
                AssetDatabase.SaveAssets();
            }

            return material;
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
