using UnityEngine;

namespace CGVR.Exp9
{
    // Changes the object to the next colour in the list each time the player clicks on it
    [RequireComponent(typeof(Tint))]
    public class ColorChanger : MonoBehaviour
    {
        static readonly Color[] Palette =
        {
            new Color(0.90f, 0.20f, 0.20f),
            new Color(0.95f, 0.55f, 0.10f),
            new Color(0.95f, 0.85f, 0.15f),
            new Color(0.25f, 0.75f, 0.30f),
            new Color(0.15f, 0.75f, 0.85f),
            new Color(0.20f, 0.35f, 0.90f),
            new Color(0.60f, 0.30f, 0.85f),
            new Color(0.95f, 0.95f, 0.95f),
        };

        int index;

        public void NextColor()
        {
            index = (index + 1) % Palette.Length;

            Tint tint = GetComponent<Tint>();
            tint.color = Palette[index];
            tint.Apply();
        }
    }
}
