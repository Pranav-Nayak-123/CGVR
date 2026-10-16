using UnityEngine;

namespace CGVR.Exp9
{
    // Rotates the object continuously; the rotation is scaled by Time.deltaTime so the speed
    // is the same at any frame rate
    public class Spinner : MonoBehaviour
    {
        public Vector3 degreesPerSecond = new Vector3(0f, 90f, 0f);

        void Update()
        {
            transform.Rotate(degreesPerSecond * Time.deltaTime, Space.World);
        }
    }
}
