using UnityEngine;

namespace CGVR.Exp9
{
    // First-person player: WASD / arrow keys to walk, mouse to look, Space to jump, left click to
    // change the colour of the object in the centre of the screen, and walk into objects to push them
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        public float moveSpeed = 5f;
        public float mouseSensitivity = 2f;
        public float jumpHeight = 1.2f;
        public float gravity = -20f;
        public float pushStrength = 4f;
        public float reach = 25f;

        CharacterController controller;
        Transform view;
        float pitch;
        float verticalSpeed;

        void Start()
        {
            controller = GetComponent<CharacterController>();
            view = GetComponentInChildren<Camera>().transform;
        }

        void Update()
        {
            if (GameInput.EscapePressed())
            {
                Cursor.lockState = CursorLockMode.None;
            }

            if (GameInput.ClickPressed())
            {
                // The first click captures the mouse; after that a click interacts with the scene
                if (Cursor.lockState != CursorLockMode.Locked)
                {
                    Cursor.lockState = CursorLockMode.Locked;
                }
                else
                {
                    ChangeColourInView();
                }
            }

            if (Cursor.lockState == CursorLockMode.Locked)
            {
                Look();
            }

            Move();
        }

        void Look()
        {
            Vector2 look = GameInput.Look() * mouseSensitivity;

            // Turning left and right rotates the whole player, looking up and down only tilts the camera
            transform.Rotate(0f, look.x, 0f);
            pitch = Mathf.Clamp(pitch - look.y, -80f, 80f);
            view.localRotation = Quaternion.Euler(pitch, 0f, 0f);
        }

        void Move()
        {
            Vector2 input = GameInput.Move();
            Vector3 direction = transform.right * input.x + transform.forward * input.y;

            if (direction.sqrMagnitude > 1f)
            {
                direction.Normalize();
            }

            if (controller.isGrounded && verticalSpeed < 0f)
            {
                verticalSpeed = -2f;
            }

            if (controller.isGrounded && GameInput.JumpPressed())
            {
                // Speed needed to reach jumpHeight: v = sqrt(2 g h)
                verticalSpeed = Mathf.Sqrt(jumpHeight * -2f * gravity);
            }

            verticalSpeed += gravity * Time.deltaTime;

            Vector3 velocity = direction * moveSpeed + Vector3.up * verticalSpeed;
            controller.Move(velocity * Time.deltaTime);
        }

        void ChangeColourInView()
        {
            RaycastHit hit;
            Ray ray = new Ray(view.position, view.forward);

            if (!Physics.Raycast(ray, out hit, reach))
            {
                return;
            }

            ColorChanger changer = hit.collider.GetComponent<ColorChanger>();

            if (changer != null)
            {
                changer.NextColor();
            }
        }

        void OnControllerColliderHit(ControllerColliderHit hit)
        {
            Rigidbody body = hit.collider.attachedRigidbody;

            // Only push loose objects, and not the ones the player is standing on
            if (body == null || body.isKinematic || hit.moveDirection.y < -0.3f)
            {
                return;
            }

            Vector3 push = new Vector3(hit.moveDirection.x, 0f, hit.moveDirection.z) * pushStrength;

#if UNITY_6000_0_OR_NEWER
            body.linearVelocity = push;
#else
            body.velocity = push;
#endif
        }
    }
}
