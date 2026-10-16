using UnityEngine;

namespace CGVR.Exp8
{
    // Sends values (uniforms) from C# to the vertex and fragment shaders every frame and lets the
    // user switch the fragment shader mode with the number keys
    public class ShaderController : MonoBehaviour
    {
        public Renderer[] targets;
        public float rotationSpeed = 30f;

        static readonly string[] ModeNames =
        {
            "Interpolated vertex colours",
            "Diffuse lighting max(N . L, 0)",
            "Grayscale (luminance)",
            "Surface normals as colours",
        };

        Material material;
        float animationTime;
        float amplitude;
        int mode;
        bool paused;
        GUIStyle textStyle;

        void Start()
        {
            // One copy of the material shared by all the objects, so playing does not change the saved asset
            material = new Material(targets[0].sharedMaterial);

            foreach (Renderer target in targets)
            {
                target.sharedMaterial = material;
            }

            amplitude = material.GetFloat("_WaveAmplitude");
        }

        void Update()
        {
            int pressed = GameInput.NumberPressed();

            if (pressed > 0)
            {
                mode = pressed - 1;
            }

            if (GameInput.PausePressed())
            {
                paused = !paused;
            }

            amplitude = Mathf.Clamp(amplitude + GameInput.UpDown() * 0.1f * Time.deltaTime, 0f, 0.3f);

            if (!paused)
            {
                animationTime += Time.deltaTime;

                foreach (Renderer target in targets)
                {
                    target.transform.Rotate(0f, rotationSpeed * Time.deltaTime, 0f, Space.World);
                }
            }

            // These become the uniform variables _Mode, _AnimationTime and _WaveAmplitude in the shader
            material.SetFloat("_Mode", mode);
            material.SetFloat("_AnimationTime", animationTime);
            material.SetFloat("_WaveAmplitude", amplitude);
        }

        void OnGUI()
        {
            if (textStyle == null)
            {
                textStyle = new GUIStyle(GUI.skin.label);
                textStyle.fontSize = 14;
                textStyle.normal.textColor = Color.white;
            }

            GUI.Box(new Rect(10, 10, 470, 150), "");
            GUI.Label(
                new Rect(20, 15, 450, 145),
                "Vertex and Fragment Shaders\n" +
                "Graphics API: " + SystemInfo.graphicsDeviceType + "\n" +
                "Shader: " + (material != null ? material.shader.name : "-") + "\n" +
                "Fragment mode " + (mode + 1) + ": " + ModeNames[mode] + "\n" +
                "Vertex wave amplitude: " + amplitude.ToString("F3") + (paused ? "   (paused)" : "") + "\n" +
                "1-4: fragment mode     Up / Down: wave amplitude     Space: pause",
                textStyle
            );
        }
    }
}
