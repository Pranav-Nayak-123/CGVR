// Experiment 8: a basic vertex shader and fragment shader written by hand.
// Unity compiles this to GLSL when the project runs on OpenGL (Graphics API: OpenGLCore).
Shader "CGVR/Exp8 Vertex Fragment Shader"
{
    Properties
    {
        _BottomColor ("Bottom colour", Color) = (1, 0.25, 0.2, 1)
        _TopColor ("Top colour", Color) = (0.2, 0.45, 1, 1)
        _Mode ("Fragment mode (0 to 3)", Float) = 0
        _WaveAmplitude ("Wave amplitude", Range(0, 0.3)) = 0.08
        _WaveFrequency ("Wave frequency", Float) = 8
        _WaveSpeed ("Wave speed", Float) = 3
        _AnimationTime ("Animation time", Float) = 0
        _LightDirection ("Light direction (world)", Vector) = (0.4, 0.8, -0.5, 0)
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            // Uniforms: the same value for every vertex and pixel, set from C# by ShaderController
            float4 _BottomColor;
            float4 _TopColor;
            float _Mode;
            float _WaveAmplitude;
            float _WaveFrequency;
            float _WaveSpeed;
            float _AnimationTime;
            float4 _LightDirection;

            // Per-vertex inputs read from the mesh
            struct VertexInput
            {
                float4 position : POSITION;
                float3 normal : NORMAL;
            };

            // Outputs of the vertex shader, interpolated across each triangle by the rasteriser
            struct VertexOutput
            {
                float4 clipPosition : SV_POSITION;
                float3 color : COLOR0;
                float3 worldNormal : TEXCOORD0;
            };

            // Vertex shader: runs once for every vertex of the mesh
            VertexOutput vert(VertexInput input)
            {
                VertexOutput output;

                // Move the vertex along its normal by a travelling sine wave
                float wave = sin(input.position.y * _WaveFrequency + _AnimationTime * _WaveSpeed) * _WaveAmplitude;
                float4 displaced = input.position + float4(input.normal * wave, 0);

                // Model -> world -> camera -> clip coordinates with the model-view-projection matrix
                output.clipPosition = UnityObjectToClipPos(displaced);
                output.worldNormal = UnityObjectToWorldNormal(input.normal);

                // Vertex colour chosen by height, from the bottom colour to the top colour
                float height = saturate(input.position.y + 0.5);
                output.color = lerp(_BottomColor.rgb, _TopColor.rgb, height);

                return output;
            }

            // Fragment shader: runs once for every pixel covered by the object
            float4 frag(VertexOutput input) : SV_Target
            {
                float3 color = input.color;
                float3 normal = normalize(input.worldNormal);

                if (_Mode > 0.5 && _Mode < 1.5)
                {
                    // Mode 1: diffuse lighting, brightness follows max(N . L, 0)
                    float diffuse = max(dot(normal, normalize(_LightDirection.xyz)), 0);
                    color *= 0.25 + 0.75 * diffuse;
                }
                else if (_Mode > 1.5 && _Mode < 2.5)
                {
                    // Mode 2: grayscale using the luminance weights of red, green and blue
                    color = dot(color, float3(0.299, 0.587, 0.114));
                }
                else if (_Mode > 2.5)
                {
                    // Mode 3: show the surface normal as a colour (x, y, z -> red, green, blue)
                    color = normal * 0.5 + 0.5;
                }

                return float4(color, 1);
            }
            ENDCG
        }
    }
}
