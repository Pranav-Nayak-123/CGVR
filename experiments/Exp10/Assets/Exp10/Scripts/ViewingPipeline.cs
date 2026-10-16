using UnityEngine;

namespace CGVR.Exp10
{
    // Experiment 10: the 3D viewing pipeline worked out by hand with 4 x 4 matrices,
    //   modeling coords -(M)-> world -(V)-> camera -(P)-> clip -(divide by w)-> NDC -(viewport)-> screen,
    // for a perspective camera (left viewport) and an orthographic camera (right viewport).
    // The hand-made results are compared with what Unity's own cameras compute.
    public class ViewingPipeline : MonoBehaviour
    {
        public Transform house;
        public Camera perspectiveCamera;
        public Camera orthographicCamera;
        public Vector3 target = new Vector3(0f, 1f, 0f);
        public float distance = 7f;
        public float azimuth = 35f;
        public float elevation = 25f;
        public float fieldOfView = 60f;
        public float nearPlane = 0.3f;
        public float farPlane = 50f;
        public int tracedVertex = 8;

        class ViewResult
        {
            public Camera camera;
            public string title;
            public Matrix4x4 model;
            public Matrix4x4 view;
            public Matrix4x4 projection;
            public Vector2[] screen;
            public bool[] visible;
            public Vector4 tracedClip;
            public Vector3 tracedNdc;
            public float viewError;
            public float projectionError;
            public float screenError;
        }

        ViewResult[] results;
        GUIStyle textStyle;
        GUIStyle titleStyle;
        Texture2D markerTexture;

        void Start()
        {
            ApplyCameras();
            results = ComputeAll();
            PrintMatrices();
        }

        void Update()
        {
            Vector2 arrows = GameInput.Arrows();
            azimuth += arrows.x * 60f * Time.deltaTime;
            elevation = Mathf.Clamp(elevation + arrows.y * 40f * Time.deltaTime, -80f, 80f);
            distance = Mathf.Clamp(distance - GameInput.Zoom() * 4f * Time.deltaTime, 1f, 30f);

            ApplyCameras();
            results = ComputeAll();

            if (GameInput.PrintPressed())
            {
                PrintMatrices();
            }
        }

        public Vector3 EyePosition()
        {
            float a = azimuth * Mathf.Deg2Rad;
            float e = elevation * Mathf.Deg2Rad;

            return target + distance * new Vector3(Mathf.Cos(e) * Mathf.Sin(a), Mathf.Sin(e), -Mathf.Cos(e) * Mathf.Cos(a));
        }

        // Places both Unity cameras at the same eye position, looking at the target
        public void ApplyCameras()
        {
            Vector3 eye = EyePosition();

            foreach (Camera camera in new[] { perspectiveCamera, orthographicCamera })
            {
                camera.transform.position = eye;
                camera.transform.LookAt(target, Vector3.up);
                camera.nearClipPlane = nearPlane;
                camera.farClipPlane = farPlane;
            }

            perspectiveCamera.orthographic = false;
            perspectiveCamera.fieldOfView = fieldOfView;
            orthographicCamera.orthographic = true;
            orthographicCamera.orthographicSize = OrthographicHalfHeight();
        }

        float OrthographicHalfHeight()
        {
            // Same visible height at the target as the perspective camera
            return distance * Mathf.Tan(fieldOfView * 0.5f * Mathf.Deg2Rad);
        }

        // ---------- Stage 1: modeling transformation M = T x R x S ----------

        public static Matrix4x4 TranslationMatrix(Vector3 offset)
        {
            Matrix4x4 m = Matrix4x4.identity;
            m[0, 3] = offset.x;
            m[1, 3] = offset.y;
            m[2, 3] = offset.z;
            return m;
        }

        public static Matrix4x4 RotationYMatrix(float degrees)
        {
            float angle = degrees * Mathf.Deg2Rad;
            Matrix4x4 m = Matrix4x4.identity;
            m[0, 0] = Mathf.Cos(angle);
            m[0, 2] = Mathf.Sin(angle);
            m[2, 0] = -Mathf.Sin(angle);
            m[2, 2] = Mathf.Cos(angle);
            return m;
        }

        public static Matrix4x4 ScalingMatrix(Vector3 scale)
        {
            Matrix4x4 m = Matrix4x4.identity;
            m[0, 0] = scale.x;
            m[1, 1] = scale.y;
            m[2, 2] = scale.z;
            return m;
        }

        Matrix4x4 ModelMatrix()
        {
            return TranslationMatrix(house.localPosition) * RotationYMatrix(house.localEulerAngles.y) * ScalingMatrix(house.localScale);
        }

        // ---------- Stage 2: viewing transformation V (look-at) ----------

        public static Matrix4x4 ViewMatrix(Vector3 eye, Vector3 lookAt, Vector3 up)
        {
            // Camera axes: u points right, v points up and n points backwards (away from the target),
            // so the camera looks along -n as in OpenGL. Unity's world is left-handed, so u = up x forward
            Vector3 forward = (lookAt - eye).normalized;
            Vector3 u = Vector3.Cross(up, forward).normalized;
            Vector3 v = Vector3.Cross(forward, u);
            Vector3 n = -forward;

            // Rotation that lines up u, v, n with x, y, z, combined with moving the eye to the origin
            Matrix4x4 m = Matrix4x4.identity;
            m.SetRow(0, new Vector4(u.x, u.y, u.z, -Vector3.Dot(u, eye)));
            m.SetRow(1, new Vector4(v.x, v.y, v.z, -Vector3.Dot(v, eye)));
            m.SetRow(2, new Vector4(n.x, n.y, n.z, -Vector3.Dot(n, eye)));
            return m;
        }

        // ---------- Stage 3: projection P ----------

        public static Matrix4x4 PerspectiveMatrix(float fov, float aspect, float near, float far)
        {
            float t = 1f / Mathf.Tan(fov * 0.5f * Mathf.Deg2Rad);
            Matrix4x4 m = Matrix4x4.zero;
            m[0, 0] = t / aspect;
            m[1, 1] = t;
            m[2, 2] = (far + near) / (near - far);
            m[2, 3] = 2f * far * near / (near - far);
            m[3, 2] = -1f;
            return m;
        }

        public static Matrix4x4 OrthographicMatrix(float halfWidth, float halfHeight, float near, float far)
        {
            Matrix4x4 m = Matrix4x4.zero;
            m[0, 0] = 1f / halfWidth;
            m[1, 1] = 1f / halfHeight;
            m[2, 2] = -2f / (far - near);
            m[2, 3] = -(far + near) / (far - near);
            m[3, 3] = 1f;
            return m;
        }

        // ---------- Stages 4 and 5: clipping test, perspective division and viewport ----------

        static bool InsideViewVolume(Vector4 clip)
        {
            return Mathf.Abs(clip.x) <= clip.w && Mathf.Abs(clip.y) <= clip.w && Mathf.Abs(clip.z) <= clip.w;
        }

        static Vector3 PerspectiveDivision(Vector4 clip)
        {
            return new Vector3(clip.x / clip.w, clip.y / clip.w, clip.z / clip.w);
        }

        static Vector2 ViewportTransformation(Vector3 ndc, Rect viewport)
        {
            // NDC x and y in [-1, 1] map onto the pixel rectangle of the viewport (origin at the bottom left)
            return new Vector2(
                viewport.x + (ndc.x + 1f) * 0.5f * viewport.width,
                viewport.y + (ndc.y + 1f) * 0.5f * viewport.height
            );
        }

        ViewResult[] ComputeAll()
        {
            return new[]
            {
                Compute(perspectiveCamera, "Viewport 1: perspective projection (fov " + fieldOfView.ToString("F0") + ")"),
                Compute(orthographicCamera, "Viewport 2: orthographic (parallel) projection"),
            };
        }

        ViewResult Compute(Camera camera, string title)
        {
            Rect viewport = camera.pixelRect;
            float aspect = viewport.width / viewport.height;
            ViewResult result = new ViewResult();
            result.camera = camera;
            result.title = title;
            result.model = ModelMatrix();
            result.view = ViewMatrix(EyePosition(), target, Vector3.up);
            result.projection = camera.orthographic
                ? OrthographicMatrix(OrthographicHalfHeight() * aspect, OrthographicHalfHeight(), nearPlane, farPlane)
                : PerspectiveMatrix(fieldOfView, aspect, nearPlane, farPlane);

            int count = HouseModel.Vertices.Length;
            result.screen = new Vector2[count];
            result.visible = new bool[count];
            Matrix4x4 pvm = result.projection * result.view * result.model;

            for (int i = 0; i < count; i++)
            {
                Vector3 vertex = HouseModel.Vertices[i];
                Vector4 clip = pvm * new Vector4(vertex.x, vertex.y, vertex.z, 1f);
                result.visible[i] = InsideViewVolume(clip);

                if (clip.w <= 0f)
                {
                    continue;
                }

                Vector3 ndc = PerspectiveDivision(clip);
                result.screen[i] = ViewportTransformation(ndc, viewport);

                if (i == tracedVertex)
                {
                    result.tracedClip = clip;
                    result.tracedNdc = ndc;
                }

                // Unity's own answer for the same vertex
                Vector3 unityScreen = camera.WorldToScreenPoint(house.TransformPoint(vertex));
                result.screenError = Mathf.Max(result.screenError, Vector2.Distance(result.screen[i], unityScreen));
            }

            result.viewError = MaxDifference(result.view, camera.worldToCameraMatrix);
            result.projectionError = MaxDifference(result.projection, camera.projectionMatrix);

            return result;
        }

        static float MaxDifference(Matrix4x4 a, Matrix4x4 b)
        {
            float largest = 0f;

            for (int i = 0; i < 16; i++)
            {
                largest = Mathf.Max(largest, Mathf.Abs(a[i] - b[i]));
            }

            return largest;
        }

        void PrintMatrices()
        {
            ViewResult perspective = results[0];
            ViewResult orthographic = results[1];
            Vector3 vertex = HouseModel.Vertices[tracedVertex];
            Vector4 world = perspective.model * new Vector4(vertex.x, vertex.y, vertex.z, 1f);
            Vector4 eyeSpace = perspective.view * world;

            Debug.Log(
                "3D VIEWING PIPELINE\n" +
                "Eye " + EyePosition().ToString("F2") + ", look-at " + target.ToString("F2") + ", up (0, 1, 0)\n\n" +
                "M (modeling -> world) = T x Ry x S\n" + perspective.model.ToString("F3") + "\n" +
                "V (world -> camera)\n" + perspective.view.ToString("F3") + "\n" +
                "P perspective (camera -> clip)\n" + perspective.projection.ToString("F3") + "\n" +
                "P orthographic (camera -> clip)\n" + orthographic.projection.ToString("F3") + "\n" +
                "Vertex " + tracedVertex + " (" + HouseModel.VertexNames[tracedVertex] + ")\n" +
                "  modeling " + vertex.ToString("F3") + "\n" +
                "  world    " + world.ToString("F3") + "\n" +
                "  camera   " + eyeSpace.ToString("F3") + "\n" +
                "  clip     " + perspective.tracedClip.ToString("F3") + " / " + orthographic.tracedClip.ToString("F3") + "\n" +
                "  NDC      " + perspective.tracedNdc.ToString("F3") + " / " + orthographic.tracedNdc.ToString("F3") + "\n" +
                "  screen   " + perspective.screen[tracedVertex].ToString("F1") + " / " + orthographic.screen[tracedVertex].ToString("F1") + "\n" +
                "Largest difference from Unity: V " + perspective.viewError.ToString("F5") +
                ", P " + Mathf.Max(perspective.projectionError, orthographic.projectionError).ToString("F5") +
                ", screen " + Mathf.Max(perspective.screenError, orthographic.screenError).ToString("F3") + " px"
            );
        }

        void OnGUI()
        {
            if (results == null)
            {
                return;
            }

            if (textStyle == null)
            {
                textStyle = new GUIStyle(GUI.skin.label);
                textStyle.fontSize = 13;
                textStyle.normal.textColor = Color.white;

                titleStyle = new GUIStyle(textStyle);
                titleStyle.fontSize = 15;
                titleStyle.fontStyle = FontStyle.Bold;

                markerTexture = Texture2D.whiteTexture;
            }

            foreach (ViewResult result in results)
            {
                Rect viewport = result.camera.pixelRect;
                float top = Screen.height - viewport.yMax;

                GUI.Box(new Rect(viewport.x + 8, top + 8, 400, 26), "");
                GUI.Label(new Rect(viewport.x + 14, top + 10, 400, 24), result.title, titleStyle);

                // Red squares: screen positions worked out by hand; they should sit on the house corners
                for (int i = 0; i < result.screen.Length; i++)
                {
                    if (!result.visible[i])
                    {
                        continue;
                    }

                    Vector2 point = result.screen[i];
                    float guiY = Screen.height - point.y;
                    Color previous = GUI.color;
                    GUI.color = i == tracedVertex ? Color.yellow : Color.red;
                    GUI.DrawTexture(new Rect(point.x - 4, guiY - 4, 8, 8), markerTexture);
                    GUI.color = previous;

                    if (i == tracedVertex)
                    {
                        GUI.Label(new Rect(point.x + 6, guiY - 22, 60, 20), "V" + i, titleStyle);
                    }
                }
            }

            ViewResult perspective = results[0];
            ViewResult orthographic = results[1];
            Vector2 traced = perspective.screen[tracedVertex];

            GUI.Box(new Rect(10, Screen.height - 120, 760, 110), "");
            GUI.Label(
                new Rect(18, Screen.height - 116, 750, 106),
                "Modeling -(M)-> World -(V)-> Camera -(P)-> Clip -(divide by w)-> NDC -(viewport)-> Screen\n" +
                "Vertex " + tracedVertex + " (yellow): clip " + perspective.tracedClip.ToString("F2") +
                "   NDC " + perspective.tracedNdc.ToString("F2") + "   screen " + traced.ToString("F1") + "\n" +
                "Hand-made matrices vs Unity: largest difference V = " + perspective.viewError.ToString("F5") +
                ", P = " + Mathf.Max(perspective.projectionError, orthographic.projectionError).ToString("F5") +
                ", screen points = " + Mathf.Max(perspective.screenError, orthographic.screenError).ToString("F3") + " px\n" +
                "Arrow keys: orbit the camera     + / - : move closer / farther     M: print all matrices to the Console",
                textStyle
            );
        }
    }
}
