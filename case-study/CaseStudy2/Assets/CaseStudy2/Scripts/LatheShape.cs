using System.Collections.Generic;
using UnityEngine;

namespace CGVR.CaseStudy2
{
    public enum LatheKind
    {
        Rim,
        Tyre,
    }

    // A wheel rim or tyre made by revolving a 2D cross-section profile around the axle (the z axis).
    // The number of segments sets how finely the circle is approximated. A 4 x 4 matrix (in millimetres)
    // can be applied to every vertex, P' = M . P, which is how the Transform tab moves the rim.
    [ExecuteAlways]
    [RequireComponent(typeof(MeshFilter))]
    [RequireComponent(typeof(MeshRenderer))]
    public class LatheShape : MonoBehaviour
    {
        public LatheKind kind;
        public int segments = 32;

        // Outer radius of the rim lip in metres, used for the chordal error
        public const float RimRadius = 0.235f;

        Matrix4x4 matrixMm = Matrix4x4.identity;
        Mesh baseMesh;
        Mesh shownMesh;

        public int TriangleCount { get; private set; }

        void OnEnable()
        {
            Rebuild();
        }

        public void SetSegments(int count)
        {
            count = Mathf.Clamp(count, 3, 256);

            if (count == segments && baseMesh != null)
            {
                return;
            }

            segments = count;
            Rebuild();
        }

        public void SetMatrix(Matrix4x4 matrixInMillimetres)
        {
            matrixMm = matrixInMillimetres;
            ApplyMatrix();
        }

        void Rebuild()
        {
            baseMesh = LatheBuilder.Build(kind, segments);
            TriangleCount = baseMesh.triangles.Length / 3;
            ApplyMatrix();
        }

        void ApplyMatrix()
        {
            if (baseMesh == null)
            {
                return;
            }

            if (shownMesh == null)
            {
                shownMesh = new Mesh();
                shownMesh.name = kind + " (shown)";
                shownMesh.hideFlags = HideFlags.DontSave;
            }

            Vector3[] source = baseMesh.vertices;
            Vector3[] moved = new Vector3[source.Length];

            for (int i = 0; i < source.Length; i++)
            {
                // Metres -> millimetres, multiply by M, back to metres
                moved[i] = matrixMm.MultiplyPoint(source[i] * 1000f) / 1000f;
            }

            int[] triangles = baseMesh.triangles;

            if (matrixMm.determinant < 0f)
            {
                // A reflection turns the surface inside out, so reverse every triangle to keep the outside in front
                for (int i = 0; i < triangles.Length; i += 3)
                {
                    int swap = triangles[i + 1];
                    triangles[i + 1] = triangles[i + 2];
                    triangles[i + 2] = swap;
                }
            }

            shownMesh.Clear();
            shownMesh.vertices = moved;
            shownMesh.triangles = triangles;
            shownMesh.RecalculateNormals();
            shownMesh.RecalculateBounds();
            GetComponent<MeshFilter>().sharedMesh = shownMesh;

            MeshCollider meshCollider = GetComponent<MeshCollider>();

            if (meshCollider != null)
            {
                meshCollider.sharedMesh = null;
                meshCollider.sharedMesh = shownMesh;
            }
        }
    }

    // Builds lathe (surface of revolution) meshes from closed 2D profiles given as (radius, z) points
    public static class LatheBuilder
    {
        // Cross-section of the rim barrel: a ring 200-235 mm from the axle, 200 mm wide, with raised lips
        static readonly Vector2[] RimBarrel =
        {
            new Vector2(0.200f, -0.100f), new Vector2(0.235f, -0.100f), new Vector2(0.235f, -0.085f),
            new Vector2(0.215f, -0.070f), new Vector2(0.215f, 0.070f), new Vector2(0.235f, 0.085f),
            new Vector2(0.235f, 0.100f), new Vector2(0.200f, 0.100f),
        };

        static readonly Vector2[] RimHub =
        {
            new Vector2(0.000f, 0.020f), new Vector2(0.060f, 0.020f), new Vector2(0.060f, 0.075f), new Vector2(0.000f, 0.075f),
        };

        static readonly Vector2[] TyreProfile =
        {
            new Vector2(0.235f, -0.110f), new Vector2(0.300f, -0.115f), new Vector2(0.325f, -0.100f),
            new Vector2(0.335f, -0.050f), new Vector2(0.335f, 0.050f), new Vector2(0.325f, 0.100f),
            new Vector2(0.300f, 0.115f), new Vector2(0.235f, 0.110f),
        };

        const int SpokeCount = 5;

        public static Mesh Build(LatheKind kind, int segments)
        {
            List<Vector3> vertices = new List<Vector3>();
            List<int> triangles = new List<int>();

            if (kind == LatheKind.Tyre)
            {
                AddRevolution(TyreProfile, segments, vertices, triangles);
            }
            else
            {
                // Rim = Revolve(barrel) U Revolve(hub) U 5 spokes  (CSG union of the three parts)
                AddRevolution(RimBarrel, segments, vertices, triangles);
                AddRevolution(RimHub, segments, vertices, triangles);

                for (int i = 0; i < SpokeCount; i++)
                {
                    AddSpoke(i * 360f / SpokeCount, vertices, triangles);
                }
            }

            Mesh mesh = new Mesh();
            mesh.name = kind.ToString();
            mesh.hideFlags = HideFlags.DontSave;
            mesh.SetVertices(vertices);
            mesh.SetTriangles(triangles, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        // Rotational sweep: every edge of the profile, turned around the z axis, becomes a ring of quads
        static void AddRevolution(Vector2[] profile, int segments, List<Vector3> vertices, List<int> triangles)
        {
            Vector2[] loop = CounterClockwise(profile);

            for (int j = 0; j < loop.Length; j++)
            {
                Vector2 a = loop[j];
                Vector2 b = loop[(j + 1) % loop.Length];

                if (a.x <= 0f && b.x <= 0f)
                {
                    continue;
                }

                // For a counter-clockwise profile the outward normal of edge (dr, dz) is (dz, -dr)
                Vector2 outward = new Vector2(b.y - a.y, -(b.x - a.x));
                int start = vertices.Count;

                for (int i = 0; i <= segments; i++)
                {
                    float angle = 2f * Mathf.PI * i / segments;
                    float cos = Mathf.Cos(angle);
                    float sin = Mathf.Sin(angle);
                    vertices.Add(new Vector3(a.x * cos, a.x * sin, a.y));
                    vertices.Add(new Vector3(b.x * cos, b.x * sin, b.y));
                }

                for (int i = 0; i < segments; i++)
                {
                    float middle = 2f * Mathf.PI * (i + 0.5f) / segments;
                    Vector3 expected = new Vector3(outward.x * Mathf.Cos(middle), outward.x * Mathf.Sin(middle), outward.y);
                    AddQuad(vertices, triangles, start + 2 * i, start + 2 * i + 1, start + 2 * i + 3, start + 2 * i + 2, expected);
                }
            }
        }

        static Vector2[] CounterClockwise(Vector2[] profile)
        {
            float area = 0f;

            for (int i = 0; i < profile.Length; i++)
            {
                Vector2 a = profile[i];
                Vector2 b = profile[(i + 1) % profile.Length];
                area += a.x * b.y - b.x * a.y;
            }

            Vector2[] loop = (Vector2[])profile.Clone();

            if (area < 0f)
            {
                System.Array.Reverse(loop);
            }

            return loop;
        }

        // A spoke is a box from the hub to the barrel, turned to its place around the axle
        static void AddSpoke(float degrees, List<Vector3> vertices, List<int> triangles)
        {
            Quaternion turn = Quaternion.Euler(0f, 0f, degrees);
            float inner = 0.055f;
            float outer = 0.205f;
            float halfWidth = 0.018f;
            float back = 0.030f;
            float front = 0.060f;

            Vector3[] corners = new Vector3[8];

            for (int i = 0; i < 8; i++)
            {
                float x = (i & 1) == 0 ? inner : outer;
                float y = (i & 2) == 0 ? -halfWidth : halfWidth;
                float z = (i & 4) == 0 ? back : front;
                corners[i] = turn * new Vector3(x, y, z);
            }

            int[][] faces =
            {
                new[] { 0, 1, 3, 2 }, new[] { 4, 5, 7, 6 }, new[] { 0, 1, 5, 4 },
                new[] { 2, 3, 7, 6 }, new[] { 0, 2, 6, 4 }, new[] { 1, 3, 7, 5 },
            };
            Vector3 centre = turn * new Vector3((inner + outer) / 2f, 0f, (back + front) / 2f);

            foreach (int[] face in faces)
            {
                int start = vertices.Count;
                Vector3 faceCentre = Vector3.zero;

                foreach (int index in face)
                {
                    vertices.Add(corners[index]);
                    faceCentre += corners[index];
                }

                AddQuad(vertices, triangles, start, start + 1, start + 2, start + 3, faceCentre / 4f - centre);
            }
        }

        // Two triangles for the quad a-b-c-d, wound so that the front side faces the expected direction.
        // Unity draws the side of a triangle towards which Cross(b - a, c - a) points.
        static void AddQuad(List<Vector3> vertices, List<int> triangles, int a, int b, int c, int d, Vector3 expected)
        {
            Vector3 first = Vector3.Cross(vertices[b] - vertices[a], vertices[c] - vertices[a]);
            Vector3 second = Vector3.Cross(vertices[c] - vertices[a], vertices[d] - vertices[a]);
            Vector3 normal = first.sqrMagnitude > second.sqrMagnitude ? first : second;

            if (Vector3.Dot(normal, expected) >= 0f)
            {
                triangles.Add(a); triangles.Add(b); triangles.Add(c);
                triangles.Add(a); triangles.Add(c); triangles.Add(d);
            }
            else
            {
                triangles.Add(a); triangles.Add(c); triangles.Add(b);
                triangles.Add(a); triangles.Add(d); triangles.Add(c);
            }
        }
    }
}
