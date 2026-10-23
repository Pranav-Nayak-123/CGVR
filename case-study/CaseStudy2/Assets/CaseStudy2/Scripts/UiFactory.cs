using UnityEngine;
using UnityEngine.Events;
using UnityEngine.UI;

namespace CGVR.CaseStudy2
{
    // Builds the on-screen controls from code with Unity's standard UI, so they work with a finger on a
    // phone as well as with the mouse. The canvas scales with the screen size, so the layout is the same
    // on a laptop and a phone (best in landscape).
    public static class UiFactory
    {
        public static readonly Color PanelColor = new Color(0.08f, 0.09f, 0.12f, 0.85f);
        public static readonly Color ButtonColor = new Color(0.2f, 0.34f, 0.6f, 1f);
        public static readonly Color ActiveColor = new Color(0.92f, 0.55f, 0.12f, 1f);
        public const float ControlHeight = 40f;

        static Font font;

        public static Font LabelFont()
        {
            if (font == null)
            {
#if UNITY_2022_2_OR_NEWER
                font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
#else
                font = Resources.GetBuiltinResource<Font>("Arial.ttf");
#endif
            }

            return font;
        }

        public static Canvas CreateCanvas(Transform parent)
        {
            GameObject canvasObject = new GameObject("Case Study UI");
            canvasObject.transform.SetParent(parent, false);

            Canvas canvas = canvasObject.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvas.sortingOrder = 100;

            CanvasScaler scaler = canvasObject.AddComponent<CanvasScaler>();
            scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            scaler.referenceResolution = new Vector2(1280f, 720f);
            scaler.matchWidthOrHeight = 0.5f;

            canvasObject.AddComponent<GraphicRaycaster>();
            return canvas;
        }

        // A panel pinned to a screen corner (corner (0,1) = top left, (1,1) = top right, ...) that grows to fit
        // the controls stacked inside it
        public static RectTransform CreatePanel(Transform parent, string name, Vector2 corner, Vector2 offset, float width)
        {
            RectTransform rect = CreateRect(name, parent);
            rect.anchorMin = corner;
            rect.anchorMax = corner;
            rect.pivot = corner;
            rect.anchoredPosition = offset;
            rect.sizeDelta = new Vector2(width, 100f);

            Image background = rect.gameObject.AddComponent<Image>();
            background.color = PanelColor;

            VerticalLayoutGroup layout = rect.gameObject.AddComponent<VerticalLayoutGroup>();
            layout.padding = new RectOffset(10, 10, 10, 10);
            layout.spacing = 6f;
            layout.childControlWidth = true;
            layout.childControlHeight = true;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = false;

            ContentSizeFitter fitter = rect.gameObject.AddComponent<ContentSizeFitter>();
            fitter.verticalFit = ContentSizeFitter.FitMode.PreferredSize;
            return rect;
        }

        // A horizontal strip of equally wide buttons
        public static Transform CreateRow(Transform parent)
        {
            RectTransform rect = CreateRect("Row", parent);

            HorizontalLayoutGroup layout = rect.gameObject.AddComponent<HorizontalLayoutGroup>();
            layout.spacing = 6f;
            layout.childControlWidth = true;
            layout.childControlHeight = true;
            layout.childForceExpandWidth = true;
            layout.childForceExpandHeight = true;

            LayoutElement element = rect.gameObject.AddComponent<LayoutElement>();
            element.minHeight = ControlHeight;
            element.preferredHeight = ControlHeight;
            return rect;
        }

        public static Text CreateText(Transform parent, string value, int size, FontStyle style)
        {
            RectTransform rect = CreateRect("Text", parent);
            Text text = rect.gameObject.AddComponent<Text>();
            text.font = LabelFont();
            text.fontSize = size;
            text.fontStyle = style;
            text.color = Color.white;
            text.alignment = TextAnchor.UpperLeft;
            text.horizontalOverflow = HorizontalWrapMode.Wrap;
            text.verticalOverflow = VerticalWrapMode.Overflow;
            text.raycastTarget = false;
            text.text = value;
            return text;
        }

        public static Button CreateButton(Transform parent, string label, UnityAction onClick)
        {
            GameObject item = DefaultControls.CreateButton(new DefaultControls.Resources());
            item.name = "Button " + label;
            item.transform.SetParent(parent, false);
            item.GetComponent<Image>().color = ButtonColor;

            Text text = item.GetComponentInChildren<Text>();

            if (text == null)
            {
                text = CreateText(item.transform, label, 16, FontStyle.Normal);
                Stretch(text.rectTransform);
            }

            text.font = LabelFont();
            text.fontSize = 16;
            text.color = Color.white;
            text.alignment = TextAnchor.MiddleCenter;
            text.text = label;

            LayoutElement element = item.AddComponent<LayoutElement>();
            element.minHeight = ControlHeight;
            element.preferredHeight = ControlHeight;
            element.flexibleWidth = 1f;

            Button button = item.GetComponent<Button>();
            button.onClick.AddListener(onClick);
            return button;
        }

        public static void SetButtonLabel(Button button, string label)
        {
            Text text = button.GetComponentInChildren<Text>();

            if (text != null)
            {
                text.text = label;
            }
        }

        public static void SetButtonColor(Button button, Color color)
        {
            button.GetComponent<Image>().color = color;
        }

        public static Slider CreateSlider(Transform parent, float min, float max, float value, bool wholeNumbers, UnityAction<float> onChange)
        {
            GameObject item = DefaultControls.CreateSlider(new DefaultControls.Resources());
            item.name = "Slider";
            item.transform.SetParent(parent, false);

            Slider slider = item.GetComponent<Slider>();
            slider.minValue = min;
            slider.maxValue = max;
            slider.wholeNumbers = wholeNumbers;
            slider.value = value;

            SetImageColor(item.transform, "Background", new Color(0.3f, 0.3f, 0.36f));
            SetImageColor(item.transform, "Fill Area/Fill", new Color(0.3f, 0.55f, 0.95f));
            SetImageColor(item.transform, "Handle Slide Area/Handle", Color.white);

            LayoutElement element = item.AddComponent<LayoutElement>();
            element.minHeight = 30f;
            element.preferredHeight = 30f;

            slider.onValueChanged.AddListener(onChange);
            return slider;
        }

        public static Toggle CreateToggle(Transform parent, string label, bool isOn, UnityAction<bool> onChange)
        {
            GameObject item = DefaultControls.CreateToggle(new DefaultControls.Resources());
            item.name = "Toggle " + label;
            item.transform.SetParent(parent, false);

            Text text = item.GetComponentInChildren<Text>();

            if (text != null)
            {
                text.font = LabelFont();
                text.fontSize = 16;
                text.color = Color.white;
                text.text = label;
            }

            SetImageColor(item.transform, "Background", Color.white);
            SetImageColor(item.transform, "Background/Checkmark", new Color(0.2f, 0.5f, 0.95f));

            LayoutElement element = item.AddComponent<LayoutElement>();
            element.minHeight = 32f;
            element.preferredHeight = 32f;

            Toggle toggle = item.GetComponent<Toggle>();
            toggle.isOn = isOn;
            toggle.onValueChanged.AddListener(onChange);
            return toggle;
        }

        // 16 text cells in a 4 x 4 grid to show a matrix
        public static Text[] CreateMatrixGrid(Transform parent, out GameObject grid)
        {
            RectTransform rect = CreateRect("Matrix", parent);
            grid = rect.gameObject;

            GridLayoutGroup layout = grid.AddComponent<GridLayoutGroup>();
            layout.cellSize = new Vector2(84f, 22f);
            layout.spacing = new Vector2(4f, 2f);
            layout.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
            layout.constraintCount = 4;

            LayoutElement element = grid.AddComponent<LayoutElement>();
            element.minHeight = 96f;
            element.preferredHeight = 96f;

            Text[] cells = new Text[16];

            for (int i = 0; i < 16; i++)
            {
                cells[i] = CreateText(grid.transform, "0", 16, FontStyle.Bold);
                cells[i].alignment = TextAnchor.MiddleRight;
                cells[i].color = new Color(1f, 0.85f, 0.4f);
            }

            return cells;
        }

        public static void ShowMatrix(Text[] cells, Matrix4x4 matrix, string format)
        {
            for (int row = 0; row < 4; row++)
            {
                for (int column = 0; column < 4; column++)
                {
                    float value = matrix[row, column];
                    cells[row * 4 + column].text = (Mathf.Abs(value) < 0.0005f ? 0f : value).ToString(format);
                }
            }
        }

        public static RectTransform CreateRect(string name, Transform parent)
        {
            GameObject item = new GameObject(name, typeof(RectTransform));
            item.transform.SetParent(parent, false);
            return item.GetComponent<RectTransform>();
        }

        static void Stretch(RectTransform rect)
        {
            rect.anchorMin = Vector2.zero;
            rect.anchorMax = Vector2.one;
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
        }

        static void SetImageColor(Transform root, string path, Color color)
        {
            Transform child = root.Find(path);

            if (child != null && child.GetComponent<Image>() != null)
            {
                child.GetComponent<Image>().color = color;
            }
        }
    }
}
