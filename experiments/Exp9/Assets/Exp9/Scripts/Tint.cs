using UnityEngine;

namespace CGVR.Exp9
{
    // Gives an object its own colour without creating a new material. The colour is set on both
    // _Color (built-in render pipeline) and _BaseColor (URP), and it also shows in edit mode
    [ExecuteAlways]
    [RequireComponent(typeof(Renderer))]
    public class Tint : MonoBehaviour
    {
        public Color color = Color.white;

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
            Renderer target = GetComponent<Renderer>();

            if (target == null)
            {
                return;
            }

            MaterialPropertyBlock block = new MaterialPropertyBlock();
            target.GetPropertyBlock(block);
            block.SetColor("_Color", color);
            block.SetColor("_BaseColor", color);
            target.SetPropertyBlock(block);
        }
    }
}
