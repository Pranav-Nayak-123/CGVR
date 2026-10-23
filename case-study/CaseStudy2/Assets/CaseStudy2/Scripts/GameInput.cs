using System.Collections.Generic;
using UnityEngine;
#if !ENABLE_LEGACY_INPUT_MANAGER && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;
#endif

namespace CGVR.CaseStudy2
{
    // Reads fingers on a touch screen (phone browser) or the mouse (laptop), through the old Input Manager
    // when it is enabled and through the new Input System package otherwise
    public static class GameInput
    {
        // Screen positions of every finger touching the screen, or of the mouse while its left button is held
        public static void GetPointers(List<Vector2> into)
        {
            into.Clear();
#if ENABLE_LEGACY_INPUT_MANAGER
            if (Input.touchCount > 0)
            {
                for (int i = 0; i < Input.touchCount; i++)
                {
                    Touch touch = Input.GetTouch(i);

                    if (touch.phase != TouchPhase.Ended && touch.phase != TouchPhase.Canceled)
                    {
                        into.Add(touch.position);
                    }
                }

                return;
            }

            if (Input.GetMouseButton(0))
            {
                into.Add(Input.mousePosition);
            }
#elif ENABLE_INPUT_SYSTEM
            Touchscreen touchscreen = Touchscreen.current;

            if (touchscreen != null)
            {
                foreach (TouchControl touch in touchscreen.touches)
                {
                    if (touch.press.isPressed)
                    {
                        into.Add(touch.position.ReadValue());
                    }
                }

                if (into.Count > 0)
                {
                    return;
                }
            }

            Mouse mouse = Mouse.current;

            if (mouse != null && mouse.leftButton.isPressed)
            {
                into.Add(mouse.position.ReadValue());
            }
#endif
        }

        // +1 when the mouse wheel turns forward this frame, -1 when it turns back, otherwise 0
        public static float Scroll()
        {
            float value = 0f;
#if ENABLE_LEGACY_INPUT_MANAGER
            value = Input.mouseScrollDelta.y;
#elif ENABLE_INPUT_SYSTEM
            if (Mouse.current != null)
            {
                value = Mouse.current.scroll.ReadValue().y;
            }
#endif
            return value > 0f ? 1f : value < 0f ? -1f : 0f;
        }
    }
}
