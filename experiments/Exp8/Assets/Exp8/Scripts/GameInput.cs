using UnityEngine;
#if !ENABLE_LEGACY_INPUT_MANAGER && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace CGVR.Exp8
{
    // Reads the keyboard through the old Input Manager when it is enabled, and through the new
    // Input System package otherwise (some Unity 6 project templates switch the old one off)
    public static class GameInput
    {
        // Returns 1 to 4 when that number key was pressed this frame, otherwise 0
        public static int NumberPressed()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKeyDown(KeyCode.Alpha1) || Input.GetKeyDown(KeyCode.Keypad1)) return 1;
            if (Input.GetKeyDown(KeyCode.Alpha2) || Input.GetKeyDown(KeyCode.Keypad2)) return 2;
            if (Input.GetKeyDown(KeyCode.Alpha3) || Input.GetKeyDown(KeyCode.Keypad3)) return 3;
            if (Input.GetKeyDown(KeyCode.Alpha4) || Input.GetKeyDown(KeyCode.Keypad4)) return 4;
#elif ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;

            if (keyboard != null)
            {
                if (keyboard.digit1Key.wasPressedThisFrame || keyboard.numpad1Key.wasPressedThisFrame) return 1;
                if (keyboard.digit2Key.wasPressedThisFrame || keyboard.numpad2Key.wasPressedThisFrame) return 2;
                if (keyboard.digit3Key.wasPressedThisFrame || keyboard.numpad3Key.wasPressedThisFrame) return 3;
                if (keyboard.digit4Key.wasPressedThisFrame || keyboard.numpad4Key.wasPressedThisFrame) return 4;
            }
#endif
            return 0;
        }

        public static bool PausePressed()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            return Input.GetKeyDown(KeyCode.Space);
#elif ENABLE_INPUT_SYSTEM
            return Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame;
#else
            return false;
#endif
        }

        // +1 while the up arrow is held, -1 while the down arrow is held
        public static float UpDown()
        {
            float value = 0f;
#if ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKey(KeyCode.UpArrow)) value += 1f;
            if (Input.GetKey(KeyCode.DownArrow)) value -= 1f;
#elif ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;

            if (keyboard != null)
            {
                if (keyboard.upArrowKey.isPressed) value += 1f;
                if (keyboard.downArrowKey.isPressed) value -= 1f;
            }
#endif
            return value;
        }
    }
}
