using UnityEngine;

namespace CGVR.Exp9
{
    // Builds the whole interactive scene from code. The menu CGVR Lab > Exp 9 creates it in the editor
    // (where it can be inspected in the Hierarchy and saved), and the R key rebuilds it while playing
    public static class SceneBuilder
    {
        public const string RootName = "Exp9 Interactive Scene";
        const int CoinCount = 5;
        const float CoinRingRadius = 9f;

        public static GameObject Build()
        {
            RemoveOldScene();
            DisableTemplateObjects();

            GameObject root = new GameObject(RootName);
            LabGame game = root.AddComponent<LabGame>();
            Transform parent = root.transform;

            game.lamp = CreateLighting(parent);
            CreateGround(parent);
            CreateWalls(parent);
            CreateCentrePiece(parent);
            CreateColourCubes(parent);
            CreatePhysicsObjects(parent);
            game.totalCoins = CreateCoins(parent);
            CreatePlayer(parent);

            return root;
        }

        static void RemoveOldScene()
        {
            GameObject old = GameObject.Find(RootName);

            if (old == null)
            {
                return;
            }

            old.name = RootName + " (old)";

            if (Application.isPlaying)
            {
                Object.Destroy(old);
            }
            else
            {
                Object.DestroyImmediate(old);
            }
        }

        static void DisableTemplateObjects()
        {
            // A new Unity scene already has a Main Camera and a Directional Light; this scene brings its own
            Camera templateCamera = Camera.main;

            if (templateCamera != null && templateCamera.GetComponentInParent<LabGame>() == null)
            {
                templateCamera.gameObject.SetActive(false);
            }

            GameObject templateLight = GameObject.Find("Directional Light");

            if (templateLight != null)
            {
                templateLight.SetActive(false);
            }
        }

        static GameObject CreateObject(PrimitiveType type, string name, Transform parent, Vector3 position, Vector3 scale, Color color)
        {
            GameObject item = GameObject.CreatePrimitive(type);
            item.name = name;
            item.transform.SetParent(parent, false);
            item.transform.localPosition = position;
            item.transform.localScale = scale;

            Tint tint = item.AddComponent<Tint>();
            tint.color = color;
            tint.Apply();

            return item;
        }

        static Light CreateLighting(Transform parent)
        {
            GameObject sun = new GameObject("Sun");
            sun.transform.SetParent(parent, false);
            sun.transform.localRotation = Quaternion.Euler(50f, -30f, 0f);

            Light sunLight = sun.AddComponent<Light>();
            sunLight.type = LightType.Directional;
            sunLight.intensity = 1.1f;
            sunLight.shadows = LightShadows.Soft;

            Vector3 lampPosition = new Vector3(-7f, 3.1f, -6f);
            CreateObject(PrimitiveType.Cylinder, "Lamp Post", parent, new Vector3(-7f, 1.5f, -6f), new Vector3(0.15f, 1.5f, 0.15f), new Color(0.2f, 0.2f, 0.22f));
            CreateObject(PrimitiveType.Sphere, "Lamp Bulb", parent, lampPosition, new Vector3(0.5f, 0.5f, 0.5f), new Color(1f, 0.95f, 0.6f));

            GameObject lamp = new GameObject("Lamp Light");
            lamp.transform.SetParent(parent, false);
            lamp.transform.localPosition = lampPosition;

            Light lampLight = lamp.AddComponent<Light>();
            lampLight.type = LightType.Point;
            lampLight.color = new Color(1f, 0.85f, 0.6f);
            lampLight.range = 10f;
            lampLight.intensity = 3f;

            return lampLight;
        }

        static void CreateGround(Transform parent)
        {
            // The plane primitive is 10 x 10 units, so a scale of 3 gives a 30 x 30 floor
            CreateObject(PrimitiveType.Plane, "Ground", parent, Vector3.zero, new Vector3(3f, 1f, 3f), new Color(0.35f, 0.55f, 0.35f));
        }

        static void CreateWalls(Transform parent)
        {
            Color wallColor = new Color(0.6f, 0.6f, 0.65f);

            CreateObject(PrimitiveType.Cube, "Wall North", parent, new Vector3(0f, 1f, 15f), new Vector3(30f, 2f, 0.5f), wallColor);
            CreateObject(PrimitiveType.Cube, "Wall South", parent, new Vector3(0f, 1f, -15f), new Vector3(30f, 2f, 0.5f), wallColor);
            CreateObject(PrimitiveType.Cube, "Wall East", parent, new Vector3(15f, 1f, 0f), new Vector3(0.5f, 2f, 30f), wallColor);
            CreateObject(PrimitiveType.Cube, "Wall West", parent, new Vector3(-15f, 1f, 0f), new Vector3(0.5f, 2f, 30f), wallColor);
        }

        static void CreateCentrePiece(Transform parent)
        {
            CreateObject(PrimitiveType.Cylinder, "Pedestal", parent, new Vector3(0f, 0.5f, 0f), new Vector3(1.5f, 0.5f, 1.5f), new Color(0.75f, 0.75f, 0.78f));

            GameObject spinning = CreateObject(PrimitiveType.Cube, "Spinning Cube", parent, new Vector3(0f, 2f, 0f), new Vector3(1.2f, 1.2f, 1.2f), new Color(0.6f, 0.3f, 0.85f));
            spinning.AddComponent<Spinner>().degreesPerSecond = new Vector3(20f, 60f, 0f);
            spinning.AddComponent<ColorChanger>();
        }

        static void CreateColourCubes(Transform parent)
        {
            Color[] colors = { new Color(0.9f, 0.2f, 0.2f), new Color(0.25f, 0.75f, 0.3f), new Color(0.2f, 0.35f, 0.9f) };

            for (int i = 0; i < colors.Length; i++)
            {
                Vector3 position = new Vector3(-6f + 2f * i, 0.6f, 5f);
                GameObject cube = CreateObject(PrimitiveType.Cube, "Colour Cube " + (i + 1), parent, position, new Vector3(1.2f, 1.2f, 1.2f), colors[i]);
                cube.AddComponent<ColorChanger>();
            }
        }

        static void CreatePhysicsObjects(Transform parent)
        {
            Vector3[] ballPositions = { new Vector3(4f, 0.5f, 3f), new Vector3(5.5f, 0.5f, 4f), new Vector3(7f, 0.5f, 3f) };
            Color[] ballColors = { new Color(0.95f, 0.55f, 0.1f), new Color(0.15f, 0.75f, 0.85f), new Color(0.9f, 0.4f, 0.65f) };

            for (int i = 0; i < ballPositions.Length; i++)
            {
                GameObject ball = CreateObject(PrimitiveType.Sphere, "Ball " + (i + 1), parent, ballPositions[i], Vector3.one, ballColors[i]);
                ball.AddComponent<Rigidbody>().mass = 1f;
            }

            // Two crates side by side with a third one stacked on top
            Vector3[] cratePositions = { new Vector3(5f, 0.4f, -4f), new Vector3(5.85f, 0.4f, -4f), new Vector3(5.425f, 1.2f, -4f) };

            for (int i = 0; i < cratePositions.Length; i++)
            {
                GameObject crate = CreateObject(PrimitiveType.Cube, "Crate " + (i + 1), parent, cratePositions[i], new Vector3(0.8f, 0.8f, 0.8f), new Color(0.55f, 0.38f, 0.2f));
                crate.AddComponent<Rigidbody>().mass = 2f;
            }
        }

        static int CreateCoins(Transform parent)
        {
            for (int i = 0; i < CoinCount; i++)
            {
                float angle = (90f + i * 360f / CoinCount) * Mathf.Deg2Rad;
                Vector3 position = new Vector3(CoinRingRadius * Mathf.Cos(angle), 1f, CoinRingRadius * Mathf.Sin(angle));

                // A flattened cylinder stood on its edge
                GameObject coin = CreateObject(PrimitiveType.Cylinder, "Coin " + (i + 1), parent, position, new Vector3(0.7f, 0.05f, 0.7f), new Color(1f, 0.8f, 0.1f));
                coin.transform.localRotation = Quaternion.Euler(90f, 0f, 0f);
                coin.GetComponent<Collider>().isTrigger = true;

                // A kinematic rigidbody makes sure the trigger reports the player walking into it
                coin.AddComponent<Rigidbody>().isKinematic = true;
                coin.AddComponent<Spinner>().degreesPerSecond = new Vector3(0f, 120f, 0f);
                coin.AddComponent<Collectible>();
            }

            return CoinCount;
        }

        static void CreatePlayer(Transform parent)
        {
            GameObject player = new GameObject("Player");
            player.transform.SetParent(parent, false);
            player.transform.localPosition = new Vector3(0f, 0.1f, -11f);

            CharacterController controller = player.AddComponent<CharacterController>();
            controller.height = 1.8f;
            controller.radius = 0.4f;
            controller.center = new Vector3(0f, 0.9f, 0f);

            GameObject eye = new GameObject("Player Camera");
            eye.tag = "MainCamera";
            eye.transform.SetParent(player.transform, false);
            eye.transform.localPosition = new Vector3(0f, 1.6f, 0f);

            Camera camera = eye.AddComponent<Camera>();
            camera.fieldOfView = 70f;
            camera.nearClipPlane = 0.05f;
            eye.AddComponent<AudioListener>();

            player.AddComponent<PlayerController>();
        }
    }
}
