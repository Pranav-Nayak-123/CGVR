// Case Study 2: shader for the car parts.
// - Simple lighting (diffuse + specular) computed in the fragment shader, so it looks the same in the
//   built-in render pipeline, URP and WebGL on phones.
// - A global clipping plane (_CaseStudyClipPlane) for the cutaway view: fragments on the positive side of
//   the plane are discarded, the same half-space test that clipping algorithms apply to each vertex.
// - Faces seen from behind (the inside of a part) are drawn darker, or in the cut colour during the cutaway.
// - _Cull switches back-face culling on and off from the Optimise tab.
Shader "CGVR/CaseStudy2 Clip"
{
    Properties
    {
        _Color ("Colour", Color) = (0.8, 0.8, 0.8, 1)
        _CutColor ("Cut colour", Color) = (0.85, 0.15, 0.1, 1)
        _ClipEnabled ("Clip enabled", Float) = 1
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "Queue" = "Geometry" }
        Cull [_Cull]

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma target 3.0
            #include "UnityCG.cginc"

            float4 _Color;
            float4 _CutColor;
            float _ClipEnabled;

            // Global: (nx, ny, nz, w). Points with dot(n, p) + w > 0 are cut away. All zeros = no cut.
            float4 _CaseStudyClipPlane;

            // Global: 1 while the cutaway is on (inside faces shown in the cut colour), 0 otherwise
            float _CaseStudyCutActive;

            struct VertexInput
            {
                float4 position : POSITION;
                float3 normal : NORMAL;
            };

            struct VertexOutput
            {
                float4 clipPosition : SV_POSITION;
                float3 worldPosition : TEXCOORD0;
                float3 worldNormal : TEXCOORD1;
            };

            VertexOutput vert(VertexInput input)
            {
                VertexOutput output;
                output.clipPosition = UnityObjectToClipPos(input.position);
                output.worldPosition = mul(unity_ObjectToWorld, input.position).xyz;
                output.worldNormal = UnityObjectToWorldNormal(input.normal);
                return output;
            }

            float4 frag(VertexOutput input, float facing : VFACE) : SV_Target
            {
                if (_ClipEnabled > 0.5)
                {
                    // clip() discards the fragment when its argument is negative
                    clip(-(dot(_CaseStudyClipPlane.xyz, input.worldPosition) + _CaseStudyClipPlane.w));
                }

                if (facing < 0)
                {
                    // Inside of a part: cut colour during the cutaway, otherwise a darker version of its own colour
                    return lerp(float4(_Color.rgb * 0.35, 1), _CutColor, _CaseStudyCutActive);
                }

                float3 normal = normalize(input.worldNormal);
                float3 toLight = normalize(float3(0.4, 0.8, 0.3));
                float3 toViewer = normalize(_WorldSpaceCameraPos - input.worldPosition);
                float3 halfway = normalize(toLight + toViewer);
                float diffuse = max(dot(normal, toLight), 0);
                float specular = pow(max(dot(normal, halfway), 0), 48) * 0.35;

                return float4(_Color.rgb * (0.3 + 0.7 * diffuse) + specular, 1);
            }
            ENDCG
        }
    }
}
