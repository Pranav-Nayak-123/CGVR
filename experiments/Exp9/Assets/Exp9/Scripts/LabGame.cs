using UnityEngine;

namespace CGVR.Exp9
{
    // Keeps the coin score, draws the on-screen instructions and handles the lamp and reset keys
    public class LabGame : MonoBehaviour
    {
        public int totalCoins;
        public Light lamp;

        int collected;
        GUIStyle textStyle;
        GUIStyle titleStyle;

        public void CollectCoin()
        {
            collected++;
        }

        void Update()
        {
            if (GameInput.LampPressed() && lamp != null)
            {
                lamp.enabled = !lamp.enabled;
            }

            if (GameInput.ResetPressed())
            {
                SceneBuilder.Build();
            }
        }

        void OnGUI()
        {
            if (textStyle == null)
            {
                textStyle = new GUIStyle(GUI.skin.label);
                textStyle.fontSize = 14;
                textStyle.normal.textColor = Color.white;

                titleStyle = new GUIStyle(textStyle);
                titleStyle.fontSize = 20;
                titleStyle.fontStyle = FontStyle.Bold;
                titleStyle.alignment = TextAnchor.MiddleCenter;
            }

            GUI.Box(new Rect(10, 10, 440, 165), "");
            GUI.Label(
                new Rect(20, 15, 420, 160),
                "Simple Interactive 3D Scene\n" +
                "WASD / arrow keys: walk     Mouse: look     Space: jump\n" +
                "Left click: change the colour of a cube in the centre of the screen\n" +
                "Walk into the balls and crates to push them\n" +
                "Walk through the gold coins to collect them\n" +
                "L: lamp on / off     R: reset the scene     Esc: free the mouse",
                textStyle
            );

            GUI.Box(new Rect(Screen.width - 190, 10, 180, 40), "");
            GUI.Label(new Rect(Screen.width - 190, 10, 180, 40), "Coins: " + collected + " / " + totalCoins, titleStyle);

            if (Cursor.lockState == CursorLockMode.Locked)
            {
                GUI.Label(new Rect(Screen.width / 2 - 20, Screen.height / 2 - 20, 40, 40), "+", titleStyle);
            }
            else
            {
                GUI.Label(
                    new Rect(0, Screen.height / 2 - 20, Screen.width, 40),
                    "Click in the Game view to look around",
                    titleStyle
                );
            }

            if (totalCoins > 0 && collected == totalCoins)
            {
                GUI.Label(
                    new Rect(0, Screen.height / 2 + 30, Screen.width, 40),
                    "All coins collected! Press R to play again",
                    titleStyle
                );
            }
        }
    }
}
