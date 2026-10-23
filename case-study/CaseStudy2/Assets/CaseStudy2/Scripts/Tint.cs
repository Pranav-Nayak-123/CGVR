using UnityEngine;

namespace CGVR.CaseStudy2
{
    // Gives an object its own colour (and says whether the cutaway plane may cut it) without creating a
    // new material. Works in the editor and in builds.
    [ExecuteAlways]
    [RequireComponent(typeof(Renderer))]
    public class Tint : MonoBehaviour
    {
        public Color color = Color.white;
        public bool clippable = true;

        void OnEnable()
        {
            Apply();
        }

        void OnValidate()
        {
            Apply();
        }

        public void Apply()
        {
            Apply(color);
        }

        // Shows a different colour (for example the selection highlight) without changing the stored colour
        public void Apply(Color shown)
        {
            Renderer target = GetComponent<Renderer>();

            if (target == null)
            {
                return;
            }

            MaterialPropertyBlock block = new MaterialPropertyBlock();
            target.GetPropertyBlock(block);
            block.SetColor("_Color", shown);
            block.SetColor("_BaseColor", shown);
            block.SetFloat("_ClipEnabled", clippable ? 1f : 0f);
            target.SetPropertyBlock(block);
        }
    }
}
