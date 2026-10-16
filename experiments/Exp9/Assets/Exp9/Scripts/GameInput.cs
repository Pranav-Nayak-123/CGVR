using UnityEngine;
#if !ENABLE_LEGACY_INPUT_MANAGER && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace CGVR.Exp9
{
    // Reads the keyboard and mouse through the old Input Manager when it is enabled, and through the
    // new Input System package otherwise (some Unity 6 project templates switch the old one off)
    public static class GameInput
    {
        public static Vector2 Move()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            return new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
#elif ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;

            if (keyboard == null)
            {
                return Vector2.zero;
            }

            float x = 0f;
            float y = 0f;

            if (keyboard.aKey.isPressed || keyboard.leftArrowKey.isPressed) x -= 1f;
            if (keyboard.dKey.isPressed || keyboard.rightArrowKey.isPressed) x += 1f;
            if (keyboard.sKey.isPressed || keyboard.downArrowKey.isPressed) y -= 1f;
            if (keyboard.wKey.isPressed || keyboard.upArrowKey.isPressed) y += 1f;

            return new Vector2(x, y);
#else
            return Vector2.zero;
#endif
        }

        public static Vector2 Look()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            return new Vector2(Input.GetAxis("Mouse X"), Input.GetAxis("Mouse Y"));
#elif ENABLE_INPUT_SYSTEM
            // The Input System reports mouse movement in pixels, so scale it to match "Mouse X" / "Mouse Y"
            return Mouse.current == null ? Vector2.zero : Mouse.current.delta.ReadValue() * 0.1f;
#else
            return Vector2.zero;
#endif
        }

        public static bool ClickPressed()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            return Input.GetMouseButtonDown(0);
#elif ENABLE_INPUT_SYSTEM
            return Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame;
#else
            return false;
#endif
        }

        public static bool JumpPressed()
        {
            return KeyPressed(KeyCode.Space);
        }

        public static bool LampPressed()
        {
            return KeyPressed(KeyCode.L);
        }

        public static bool ResetPressed()
        {
            return KeyPressed(KeyCode.R);
        }

        public static bool EscapePressed()
        {
            return KeyPressed(KeyCode.Escape);
        }

        static bool KeyPressed(KeyCode key)
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            return Input.GetKeyDown(key);
#elif ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;

            if (keyboard == null)
            {
                return false;
            }

            switch (key)
            {
                case KeyCode.Space:
                    return keyboard.spaceKey.wasPressedThisFrame;
                case KeyCode.L:
                    return keyboard.lKey.wasPressedThisFrame;
                case KeyCode.R:
                    return keyboard.rKey.wasPressedThisFrame;
                case KeyCode.Escape:
                    return keyboard.escapeKey.wasPressedThisFrame;
                default:
                    return false;
            }
#else
            return false;
#endif
        }
    }
}
