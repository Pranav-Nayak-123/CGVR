using System.Collections.Generic;
using UnityEngine;

namespace CGVR.Exp10
{
    // Builds the walls or the roof of the house as a mesh from HouseModel. The mesh is rebuilt
    // whenever the object is enabled, so nothing needs to be saved as an asset
    [ExecuteAlways]
    [RequireComponent(typeof(MeshFilter))]
    [RequireComponent(typeof(MeshRenderer))]
    public class HouseMesh : MonoBehaviour
    {
        public bool roof;

        void OnEnable()
        {
            Mesh mesh = new Mesh();
            mesh.name = roof ? "House Roof" : "House Walls";
            mesh.hideFlags = HideFlags.DontSave;

            List<Vector3> positions = new List<Vector3>();
            List<int> triangles = new List<int>();
            Vector3 centre = HouseModel.Centre();

            foreach (int[] face in roof ? HouseModel.RoofFaces : HouseModel.WallFaces)
            {
                AddFace(face, centre, positions, triangles);
            }

            mesh.SetVertices(positions);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            GetComponent<MeshFilter>().sharedMesh = mesh;
        }

        static void AddFace(int[] face, Vector3 centre, List<Vector3> positions, List<int> triangles)
        {
            Vector3 a = HouseModel.Vertices[face[0]];
            Vector3 b = HouseModel.Vertices[face[1]];
            Vector3 c = HouseModel.Vertices[face[2]];
            Vector3 faceCentre = Vector3.zero;

            foreach (int index in face)
            {
                faceCentre += HouseModel.Vertices[index];
            }

            faceCentre /= face.Length;

            // Unity draws the side of a triangle whose vertices appear clockwise, which is the side
            // that Cross(b - a, c - a) points to. Reverse the face if that side points into the house
            bool reverse = Vector3.Dot(Vector3.Cross(b - a, c - a), faceCentre - centre) < 0f;
            int start = positions.Count;

            for (int i = 0; i < face.Length; i++)
            {
                int index = reverse ? face[face.Length - 1 - i] : face[i];
                positions.Add(HouseModel.Vertices[index]);
            }

            // Split the polygon into a fan of triangles from its first vertex
            for (int i = 1; i < face.Length - 1; i++)
            {
                triangles.Add(start);
                triangles.Add(start + i);
                triangles.Add(start + i + 1);
            }
        }
    }
}
