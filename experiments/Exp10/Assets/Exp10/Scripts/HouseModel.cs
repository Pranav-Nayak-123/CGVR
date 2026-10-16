using UnityEngine;

namespace CGVR.Exp10
{
    // The house in its own modeling coordinates: a 2 x 1.4 x 2 box with a roof whose ridge is at y = 2.2
    public static class HouseModel
    {
        public static readonly Vector3[] Vertices =
        {
            new Vector3(-1f, 0f, 1f), new Vector3(1f, 0f, 1f), new Vector3(1f, 1.4f, 1f), new Vector3(-1f, 1.4f, 1f),
            new Vector3(-1f, 0f, -1f), new Vector3(1f, 0f, -1f), new Vector3(1f, 1.4f, -1f), new Vector3(-1f, 1.4f, -1f),
            new Vector3(0f, 2.2f, 1f), new Vector3(0f, 2.2f, -1f),
        };

        public static readonly string[] VertexNames =
        {
            "front bottom left", "front bottom right", "front top right", "front top left",
            "back bottom left", "back bottom right", "back top right", "back top left",
            "front roof peak", "back roof peak",
        };

        // Each face is a list of vertex numbers
        public static readonly int[][] WallFaces =
        {
            new[] { 0, 1, 2, 3 },
            new[] { 5, 4, 7, 6 },
            new[] { 4, 0, 3, 7 },
            new[] { 1, 5, 6, 2 },
            new[] { 4, 5, 1, 0 },
        };

        public static readonly int[][] RoofFaces =
        {
            new[] { 3, 2, 8 },
            new[] { 6, 7, 9 },
            new[] { 3, 8, 9, 7 },
            new[] { 8, 2, 6, 9 },
        };

        public static Vector3 Centre()
        {
            Vector3 sum = Vector3.zero;

            foreach (Vector3 vertex in Vertices)
            {
                sum += vertex;
            }

            return sum / Vertices.Length;
        }
    }
}
