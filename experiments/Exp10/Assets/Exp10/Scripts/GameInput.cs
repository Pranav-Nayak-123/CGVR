using UnityEngine;
#if !ENABLE_LEGACY_INPUT_MANAGER && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace CGVR.Exp10
{
    // Reads the keyboard through the old Input Manager when it is enabled, and through the new
    // Input System package otherwise (some Unity 6 project templates switch the old one off)
    public static class GameInput
    {
        // Arrow keys held down: x = left / right, y = up / down
        public static Vector2 Arrows()
        {
            Vector2 value = Vector2.zero;
#if ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKey(KeyCode.LeftArrow)) value.x -= 1f;
            if (Input.GetKey(KeyCode.RightArrow)) value.x += 1f;
            if (Input.GetKey(KeyCode.DownArrow)) value.y -= 1f;
            if (Input.GetKey(KeyCode.UpArrow)) value.y += 1f;
#elif ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;

            if (keyboard != null)
            {
                if (keyboard.leftArrowKey.isPressed) value.x -= 1f;
                if (keyboard.rightArrowKey.isPressed) value.x += 1f;
                if (keyboard.downArrowKey.isPressed) value.y -= 1f;
                if (keyboard.upArrowKey.isPressed) value.y += 1f;
            }
#endif
            return value;
        }

        // +1 while + (or =) is held to move closer, -1 while - is held to move away
        public static float Zoom()
        {
            float value = 0f;
#if ENABLE_LEGACY_INPUT_MANAGER
            if (Input.GetKey(KeyCode.Equals) || Input.GetKey(KeyCode.Plus) || Input.GetKey(KeyCode.KeypadPlus)) value += 1f;
            if (Input.GetKey(KeyCode.Minus) || Input.GetKey(KeyCode.KeypadMinus)) value -= 1f;
#elif ENABLE_INPUT_SYSTEM
            Keyboard keyboard = Keyboard.current;

            if (keyboard != null)
            {
                if (keyboard.equalsKey.isPressed || keyboard.numpadPlusKey.isPressed) value += 1f;
                if (keyboard.minusKey.isPressed || keyboard.numpadMinusKey.isPressed) value -= 1f;
            }
#endif
            return value;
        }

        public static bool PrintPressed()
        {
#if ENABLE_LEGACY_INPUT_MANAGER
            return Input.GetKeyDown(KeyCode.M);
#elif ENABLE_INPUT_SYSTEM
            return Keyboard.current != null && Keyboard.current.mKey.wasPressedThisFrame;
#else
            return false;
#endif
        }
    }
}
