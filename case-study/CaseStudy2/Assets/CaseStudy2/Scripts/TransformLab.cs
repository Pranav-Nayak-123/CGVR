using System.Collections.Generic;
using UnityEngine;

namespace CGVR.CaseStudy2
{
    public enum StepType
    {
        Scale,
        Rotate,
        Translate,
        Reflect,
        Shear,
    }

    // One transformation in the sequence. value = scale factor, angle in degrees, distance in mm or shear factor
    public class TransformStep
    {
        public StepType type;
        public float value;
        public int axis;

        static readonly string[] AxisNames = { "X", "Y", "Z" };

        public TransformStep(StepType type, float value, int axis)
        {
            this.type = type;
            this.value = value;
            this.axis = axis;
        }

        public string Describe()
        {
            string axisName = AxisNames[axis];

            switch (type)
            {
                case StepType.Scale:
                    return "S(" + value.ToString("0.##") + ")";
                case StepType.Rotate:
                    return "R" + axisName.ToLower() + "(" + value.ToString("0.#") + " deg)";
                case StepType.Translate:
                    return "T(" + value.ToString("+0.#;-0.#;0") + " mm along " + axisName + ")";
                case StepType.Reflect:
                    return "Reflect (" + axisName + " -> -" + axisName + ")";
                default:
                    return "Shear (" + axisName.ToLower() + " += " + value.ToString("0.##") + " " + AxisNames[(axis + 1) % 3].ToLower() + ")";
            }
        }
    }

    // A sequence of transformations M1, M2, ..., Mn applied to the wheel rim, in homogeneous coordinates.
    // The composite matrix is C = Mn ... M2 . M1 (column vectors, P' = C . P), with distances in millimetres.
    public class TransformLab
    {
        public readonly List<TransformStep> steps = new List<TransformStep>();

        // -1 when not animating, otherwise the animation time measured in steps (1 second per step)
        float animation = -1f;

        public bool Animating
        {
            get { return animation >= 0f; }
        }

        // The case study: scale the rim by 1.5, rotate it 45 degrees about the axle (Z), move it 50 mm forward (X)
        public void LoadPreset()
        {
            steps.Clear();
            steps.Add(new TransformStep(StepType.Scale, 1.5f, 2));
            steps.Add(new TransformStep(StepType.Rotate, 45f, 2));
            steps.Add(new TransformStep(StepType.Translate, 50f, 0));
            animation = -1f;
        }

        public void StartAnimation()
        {
            animation = steps.Count > 0 ? 0f : -1f;
        }

        public void Advance(float seconds)
        {
            if (!Animating)
            {
                return;
            }

            animation += seconds;

            if (animation >= steps.Count)
            {
                animation = -1f;
            }
        }

        public void SwapLastTwo()
        {
            int count = steps.Count;

            if (count >= 2)
            {
                TransformStep last = steps[count - 1];
                steps[count - 1] = steps[count - 2];
                steps[count - 2] = last;
            }
        }

        // The matrix to show now: the full composite, or the partly finished one while animating
        public Matrix4x4 CurrentMatrix()
        {
            if (!Animating)
            {
                return Composite();
            }

            int done = Mathf.FloorToInt(animation);
            Matrix4x4 result = Matrix4x4.identity;

            for (int k = 0; k < done; k++)
            {
                result = StepMatrix(steps[k], 1f) * result;
            }

            return StepMatrix(steps[done], animation - done) * result;
        }

        // C = Mn ... M2 . M1: each new matrix multiplies on the left, so M1 acts on the point first
        public Matrix4x4 Composite()
        {
            Matrix4x4 result = Matrix4x4.identity;

            foreach (TransformStep step in steps)
            {
                result = StepMatrix(step, 1f) * result;
            }

            return result;
        }

        // The same matrices multiplied in the wrong order, M1 . M2 ... Mn, so Mn acts first
        public Matrix4x4 WrongOrder()
        {
            Matrix4x4 result = Matrix4x4.identity;

            foreach (TransformStep step in steps)
            {
                result = result * StepMatrix(step, 1f);
            }

            return result;
        }

        // The composite built with Unity's own matrix functions, to check the hand-made matrices
        public Matrix4x4 UnityComposite()
        {
            Matrix4x4 result = Matrix4x4.identity;

            foreach (TransformStep step in steps)
            {
                Vector3 direction = AxisVector(step.axis);
                Matrix4x4 m;

                switch (step.type)
                {
                    case StepType.Scale:
                        m = Matrix4x4.Scale(Vector3.one * step.value);
                        break;
                    case StepType.Rotate:
                        m = Matrix4x4.Rotate(Quaternion.AngleAxis(step.value, direction));
                        break;
                    case StepType.Translate:
                        m = Matrix4x4.Translate(direction * step.value);
                        break;
                    case StepType.Reflect:
                        m = Matrix4x4.Scale(Vector3.one - 2f * direction);
                        break;
                    default:
                        // Unity has no shear function, so the hand-made matrix is used for this step
                        m = StepMatrix(step, 1f);
                        break;
                }

                result = m * result;
            }

            return result;
        }

        // The 4 x 4 homogeneous matrix of one step; t from 0 to 1 gives the in-between matrices for animation
        public static Matrix4x4 StepMatrix(TransformStep step, float t)
        {
            Matrix4x4 m = Matrix4x4.identity;
            int a = step.axis;

            switch (step.type)
            {
                case StepType.Scale:
                    float factor = Mathf.Lerp(1f, step.value, t);
                    m[0, 0] = factor;
                    m[1, 1] = factor;
                    m[2, 2] = factor;
                    break;

                case StepType.Rotate:
                    float angle = step.value * t * Mathf.Deg2Rad;
                    float cos = Mathf.Cos(angle);
                    float sin = Mathf.Sin(angle);
                    // The two axes that turn: for Z they are X and Y, for X they are Y and Z, for Y they are Z and X
                    int p = (a + 1) % 3;
                    int q = (a + 2) % 3;
                    m[p, p] = cos;
                    m[p, q] = -sin;
                    m[q, p] = sin;
                    m[q, q] = cos;
                    break;

                case StepType.Translate:
                    m[a, 3] = step.value * t;
                    break;

                case StepType.Reflect:
                    m[a, a] = Mathf.Lerp(1f, -1f, t);
                    break;

                case StepType.Shear:
                    m[a, (a + 1) % 3] = step.value * t;
                    break;
            }

            return m;
        }

        public static Vector3 AxisVector(int axis)
        {
            return axis == 0 ? Vector3.right : axis == 1 ? Vector3.up : Vector3.forward;
        }

        public static float MaxDifference(Matrix4x4 a, Matrix4x4 b)
        {
            float largest = 0f;

            for (int i = 0; i < 16; i++)
            {
                largest = Mathf.Max(largest, Mathf.Abs(a[i] - b[i]));
            }

            return largest;
        }
    }
}
