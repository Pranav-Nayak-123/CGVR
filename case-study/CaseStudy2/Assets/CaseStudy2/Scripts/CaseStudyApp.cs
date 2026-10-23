using System.Collections.Generic;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Rendering;
using UnityEngine.UI;

namespace CGVR.CaseStudy2
{
    // Case Study 2: VR collaborative car design (Bengaluru and Detroit teams). An interactive 1:1 car
    // prototype with four tabs, one for each part of the answer:
    //   1 Modelling  - CSG union of primitives, wheels made by revolving 2D profiles, tessellation vs error
    //   2 Transform  - build any sequence of 4 x 4 homogeneous transformations and apply it to the wheel rim
    //   3 Optimise   - stereo (two-eye) view, back-face culling, frustum-culling counts, LOD, near-plane clipping
    //   4 Cutaway    - a clipping plane that cuts the car open
    // Everything works with touch (phone browser) as well as the mouse.
    public class CaseStudyApp : MonoBehaviour
    {
        public Camera leftEye;
        public Camera rightEye;
        public Transform car;
        public LatheShape studiedRim;
        public LatheShape ghostRim;
        public LatheShape[] rims;
        public Material carMaterial;
        public Transform bengaluruMarker;
        public Transform detroitMarker;

        const float EyeSeparation = 0.064f;
        const float VrBudgetMs = 1000f / 90f;
        static readonly string[] TabNames = { "Modelling", "Transform", "Optimise", "Cutaway" };
        static readonly string[] AxisNames = { "X (forward)", "Y (up)", "Z (axle)" };

        // Camera
        readonly Vector3 orbitTarget = new Vector3(0f, 0.7f, 0f);
        float yaw = 215f;
        float pitch = 18f;
        float distance = 7f;
        float insideYaw = 90f;
        float insidePitch = 5f;
        bool insideCabin;
        bool stereo;
        float nearPlane = 0.05f;

        // User interface
        Canvas canvas;
        int activeTab;
        bool panelsHidden;
        Button[] tabButtons;
        GameObject[] tabPanels;
        GameObject infoPanel;
        Text infoTitle;
        Text infoText;
        Text[] matrixCells;
        GameObject matrixGrid;
        Text bengaluruLabel;
        Text detroitLabel;
        Text segmentsLabel;
        Text scaleLabel;
        Text angleLabel;
        Text moveLabel;
        Text nearLabel;
        Text cutLabel;
        Button axisButton;
        Button cutAxisButton;

        // Modelling, transformations, optimisation and cutaway settings
        int rimSegments = 32;
        bool lodWheels;
        readonly TransformLab lab = new TransformLab();
        float stepScale = 1.5f;
        float stepAngle = 45f;
        float stepMove = 50f;
        int stepAxis = 2;
        bool showGhost;
        bool backFaceCulling;
        bool cutaway;
        int cutAxis;
        float cutPosition = 0.3f;

        // Selected part
        Tint selected;
        Vector3 selectedStartPosition;
        Quaternion selectedStartRotation;
        Vector3 selectedStartScale;

        // Touch gestures
        readonly List<Vector2> pointers = new List<Vector2>();
        readonly List<Vector2> previous = new List<Vector2>();
        readonly List<RaycastResult> uiHits = new List<RaycastResult>();
        bool gestureOnUi;
        float pressTime;
        float pressTravel;

        // Statistics
        Renderer[] parts;
        float frameTime = 1f / 60f;
        float statsTimer;
        string statsText = "";

        void Start()
        {
            Application.targetFrameRate = 60;
            EnsureEventSystem();
            parts = car.GetComponentsInChildren<Renderer>();
            BuildInterface();
            lab.LoadPreset();
            ApplyTransformations();
            SetBackFaceCulling(false);
            UpdateCutaway();
            ShowTab(0);
        }

        void OnDisable()
        {
            // Leave the shared material and the global clipping plane as they were before playing
            if (carMaterial != null)
            {
                carMaterial.SetFloat("_Cull", (float)CullMode.Off);
            }

            Shader.SetGlobalVector("_CaseStudyClipPlane", Vector4.zero);
            Shader.SetGlobalFloat("_CaseStudyCutActive", 0f);
        }

        void Update()
        {
            frameTime = Mathf.Lerp(frameTime, Time.unscaledDeltaTime, 0.05f);
            HandleGestures();

            if (lab.Animating)
            {
                lab.Advance(Time.deltaTime);
                ApplyTransformations();
            }

            if (lodWheels)
            {
                UpdateWheelLod();
            }

            PlaceCameras();
            PlaceMarkerLabels();

            statsTimer -= Time.unscaledDeltaTime;

            if (statsTimer <= 0f)
            {
                statsTimer = 0.25f;
                statsText = ComputeStatistics();
            }

            RefreshInfo();
        }

        // ---------------- Camera ----------------

        void PlaceCameras()
        {
            Vector3 eye;
            Quaternion rotation;

            if (insideCabin)
            {
                // Driver's head position; the car faces +X
                eye = car.TransformPoint(new Vector3(-0.15f, 1.12f, 0.35f));
                rotation = Quaternion.Euler(insidePitch, insideYaw, 0f);
            }
            else
            {
                rotation = Quaternion.Euler(pitch, yaw, 0f);
                eye = orbitTarget - rotation * Vector3.forward * distance;
            }

            Vector3 right = rotation * Vector3.right;

            if (stereo)
            {
                // Two eyes 64 mm apart, each drawn on its own half of the screen like a headset's two displays
                leftEye.transform.SetPositionAndRotation(eye - right * EyeSeparation / 2f, rotation);
                rightEye.transform.SetPositionAndRotation(eye + right * EyeSeparation / 2f, rotation);
                leftEye.rect = new Rect(0f, 0f, 0.5f, 1f);
                rightEye.rect = new Rect(0.5f, 0f, 0.5f, 1f);
                rightEye.enabled = true;
            }
            else
            {
                leftEye.transform.SetPositionAndRotation(eye, rotation);
                leftEye.rect = new Rect(0f, 0f, 1f, 1f);
                rightEye.enabled = false;
            }

            leftEye.nearClipPlane = nearPlane;
            rightEye.nearClipPlane = nearPlane;
        }

        // ---------------- Touch and mouse gestures ----------------

        void HandleGestures()
        {
            GameInput.GetPointers(pointers);

            if (pointers.Count != previous.Count)
            {
                if (previous.Count == 0)
                {
                    // A new gesture: ignore it if it started on a button, slider or panel
                    gestureOnUi = OverInterface(pointers[0]);
                    pressTime = Time.unscaledTime;
                    pressTravel = 0f;
                }
                else if (pointers.Count == 0 && previous.Count == 1 && !gestureOnUi
                         && Time.unscaledTime - pressTime < 0.35f && pressTravel < 12f)
                {
                    Tap(previous[0]);
                }

                previous.Clear();
                previous.AddRange(pointers);
            }
            else if (pointers.Count == 1)
            {
                Vector2 delta = pointers[0] - previous[0];
                pressTravel += delta.magnitude;

                if (!gestureOnUi)
                {
                    Drag(delta);
                }

                previous[0] = pointers[0];
            }
            else if (pointers.Count >= 2)
            {
                pressTravel += 100f;

                if (!gestureOnUi)
                {
                    float before = Vector2.Distance(previous[0], previous[1]);
                    float after = Vector2.Distance(pointers[0], pointers[1]);
                    Pinch(before > 1f ? after / before : 1f);
                    Twist(Vector2.SignedAngle(previous[1] - previous[0], pointers[1] - pointers[0]));
                }

                previous.Clear();
                previous.AddRange(pointers);
            }

            float scroll = GameInput.Scroll();

            if (scroll != 0f)
            {
                Pinch(scroll > 0f ? 1.1f : 1f / 1.1f);
            }
        }

        bool OverInterface(Vector2 screenPosition)
        {
            if (EventSystem.current == null)
            {
                return false;
            }

            PointerEventData data = new PointerEventData(EventSystem.current);
            data.position = screenPosition;
            uiHits.Clear();
            EventSystem.current.RaycastAll(data, uiHits);
            return uiHits.Count > 0;
        }

        // One finger: orbit the camera (or look around inside the cabin), or move the selected part
        void Drag(Vector2 delta)
        {
            if (selected != null)
            {
                Camera eye = leftEye;
                float depth = Vector3.Distance(eye.transform.position, selected.transform.position);
                float metresPerPixel = 2f * depth * Mathf.Tan(eye.fieldOfView * 0.5f * Mathf.Deg2Rad) / Screen.height;
                selected.transform.position += (eye.transform.right * delta.x + eye.transform.up * delta.y) * metresPerPixel;
                return;
            }

            if (insideCabin)
            {
                insideYaw += delta.x * 0.2f;
                insidePitch = Mathf.Clamp(insidePitch - delta.y * 0.2f, -60f, 60f);
            }
            else
            {
                yaw += delta.x * 0.3f;
                pitch = Mathf.Clamp(pitch - delta.y * 0.3f, -5f, 80f);
            }
        }

        // Two fingers apart / together (or the mouse wheel): zoom, or scale the selected part
        void Pinch(float factor)
        {
            if (selected != null)
            {
                Vector3 scale = selected.transform.localScale * factor;

                if (scale.x < 20f * selectedStartScale.x && scale.x > 0.05f * selectedStartScale.x)
                {
                    selected.transform.localScale = scale;
                }

                return;
            }

            distance = Mathf.Clamp(distance / factor, 1.5f, 25f);
        }

        // Two fingers turning: rotate the selected part about the vertical axis
        void Twist(float degrees)
        {
            if (selected != null)
            {
                selected.transform.Rotate(0f, -degrees, 0f, Space.World);
            }
        }

        // A quick tap: select the car part under the finger, or clear the selection
        void Tap(Vector2 screenPosition)
        {
            Camera eye = stereo && screenPosition.x > Screen.width / 2f ? rightEye : leftEye;
            RaycastHit hit;

            if (Physics.Raycast(eye.ScreenPointToRay(screenPosition), out hit, 100f))
            {
                Tint tint = hit.collider.GetComponent<Tint>();

                if (tint != null && tint.transform.IsChildOf(car))
                {
                    Select(tint);
                    return;
                }
            }

            Select(null);
        }

        void Select(Tint part)
        {
            if (selected != null)
            {
                selected.Apply();
            }

            selected = part;

            if (selected != null)
            {
                selectedStartPosition = selected.transform.localPosition;
                selectedStartRotation = selected.transform.localRotation;
                selectedStartScale = selected.transform.localScale;
                selected.Apply(Color.Lerp(selected.color, new Color(1f, 0.85f, 0.1f), 0.65f));
            }
        }

        void ResetSelectedPart()
        {
            if (selected != null)
            {
                selected.transform.localPosition = selectedStartPosition;
                selected.transform.localRotation = selectedStartRotation;
                selected.transform.localScale = selectedStartScale;
            }
        }

        void ResetView()
        {
            insideCabin = false;
            yaw = 215f;
            pitch = 18f;
            distance = 7f;
        }

        // ---------------- Tab 1: modelling ----------------

        void SetRimSegments(int count)
        {
            rimSegments = count;

            foreach (LatheShape rim in rims)
            {
                rim.SetSegments(count);
            }

            ghostRim.SetSegments(count);
        }

        // Level of detail: wheels far from the eye use fewer segments
        void UpdateWheelLod()
        {
            foreach (LatheShape rim in rims)
            {
                float d = Vector3.Distance(leftEye.transform.position, rim.transform.position);
                int count = d < 4f ? rimSegments : d < 9f ? Mathf.Max(8, rimSegments / 2) : Mathf.Max(6, rimSegments / 4);
                rim.SetSegments(count);
            }
        }

        static float ChordalErrorMm(int segments)
        {
            // Largest gap between a circle of radius R and a polygon of N segments: R (1 - cos(pi / N))
            return LatheShape.RimRadius * 1000f * (1f - Mathf.Cos(Mathf.PI / segments));
        }

        // ---------------- Tab 2: transformations ----------------

        void AddStep(StepType type)
        {
            float value = type == StepType.Scale ? stepScale
                : type == StepType.Rotate ? stepAngle
                : type == StepType.Translate ? stepMove
                : type == StepType.Shear ? 0.5f
                : 0f;

            lab.steps.Add(new TransformStep(type, value, stepAxis));
            ApplyTransformations();
        }

        void ApplyTransformations()
        {
            studiedRim.SetMatrix(lab.CurrentMatrix());

            if (showGhost)
            {
                ghostRim.SetMatrix(lab.WrongOrder());
            }
        }

        // ---------------- Tab 3: optimisation ----------------

        void SetBackFaceCulling(bool on)
        {
            backFaceCulling = on;
            carMaterial.SetFloat("_Cull", on ? (float)CullMode.Back : (float)CullMode.Off);
        }

        string ComputeStatistics()
        {
            Plane[] planes = GeometryUtility.CalculateFrustumPlanes(leftEye);
            int partCount = 0;
            int partsInView = 0;
            long triangles = 0;
            long trianglesInView = 0;

            foreach (Renderer part in parts)
            {
                if (part == null || !part.enabled || !part.gameObject.activeInHierarchy)
                {
                    continue;
                }

                MeshFilter filter = part.GetComponent<MeshFilter>();
                long count = filter != null && filter.sharedMesh != null ? filter.sharedMesh.GetIndexCount(0) / 3 : 0;
                partCount++;
                triangles += count;

                // View-frustum culling: is the part's bounding box inside the six planes of the view volume?
                if (GeometryUtility.TestPlanesAABB(planes, part.bounds))
                {
                    partsInView++;
                    trianglesInView += count;
                }
            }

            int eyes = stereo ? 2 : 1;
            long afterBackFaces = backFaceCulling ? trianglesInView / 2 : trianglesInView;
            float milliseconds = frameTime * 1000f;

            return
                "Frame time: " + milliseconds.ToString("F1") + " ms (" + (1000f / milliseconds).ToString("F0") + " fps). " +
                "VR budget at 90 Hz: " + VrBudgetMs.ToString("F1") + " ms per frame\n" +
                "Eyes rendered: " + eyes + (stereo ? " (two cameras, 64 mm apart)" : "") + "\n\n" +
                "Parts: " + partCount + " in the scene, " + partsInView + " inside the view frustum\n" +
                "Triangles in the car: " + triangles + "\n" +
                "  after frustum culling: " + trianglesInView + "\n" +
                "  after back-face culling: about " + afterBackFaces + (backFaceCulling ? " (half face away)" : " (culling off)") + "\n" +
                "  drawn per frame for " + eyes + " eye(s): about " + afterBackFaces * eyes + "\n\n" +
                "Near clipping plane: " + nearPlane.ToString("F2") + " m. Anything closer to the eye is clipped; " +
                "sit inside the cabin and raise it to see the dashboard disappear.";
        }

        // ---------------- Tab 4: cutaway ----------------

        void UpdateCutaway()
        {
            Vector3 normal = TransformLab.AxisVector(cutAxis);

            // Plane n . p = d. The shader discards fragments with n . p - d > 0
            Shader.SetGlobalVector("_CaseStudyClipPlane", cutaway
                ? new Vector4(normal.x, normal.y, normal.z, -cutPosition)
                : Vector4.zero);
            Shader.SetGlobalFloat("_CaseStudyCutActive", cutaway ? 1f : 0f);
        }

        // ---------------- Collaborators ----------------

        void PlaceMarkerLabels()
        {
            PlaceLabel(bengaluruLabel, bengaluruMarker);
            PlaceLabel(detroitLabel, detroitMarker);
        }

        void PlaceLabel(Text label, Transform marker)
        {
            Vector3 screen = leftEye.WorldToScreenPoint(marker.position + Vector3.up * 0.3f);
            bool visible = screen.z > 0f && !insideCabin;
            label.gameObject.SetActive(visible);

            if (visible)
            {
                label.rectTransform.anchoredPosition = new Vector2(screen.x, screen.y) / canvas.scaleFactor;
            }
        }

        // ---------------- User interface ----------------

        void EnsureEventSystem()
        {
            if (EventSystem.current != null)
            {
                return;
            }

            GameObject eventSystem = new GameObject("EventSystem");
            eventSystem.AddComponent<EventSystem>();
#if ENABLE_LEGACY_INPUT_MANAGER
            eventSystem.AddComponent<StandaloneInputModule>();
#elif ENABLE_INPUT_SYSTEM
            eventSystem.AddComponent<UnityEngine.InputSystem.UI.InputSystemUIInputModule>().AssignDefaultActions();
#endif
        }

        void BuildInterface()
        {
            canvas = UiFactory.CreateCanvas(transform);
            Transform root = canvas.transform;

            // Tab bar
            RectTransform bar = UiFactory.CreateRect("Tabs", root);
            bar.anchorMin = new Vector2(0f, 1f);
            bar.anchorMax = new Vector2(0f, 1f);
            bar.pivot = new Vector2(0f, 1f);
            bar.anchoredPosition = new Vector2(10f, -10f);
            bar.sizeDelta = new Vector2(620f, UiFactory.ControlHeight);
            HorizontalLayoutGroup barLayout = bar.gameObject.AddComponent<HorizontalLayoutGroup>();
            barLayout.spacing = 6f;
            barLayout.childControlWidth = true;
            barLayout.childControlHeight = true;
            barLayout.childForceExpandWidth = true;
            barLayout.childForceExpandHeight = true;

            tabButtons = new Button[TabNames.Length];

            for (int i = 0; i < TabNames.Length; i++)
            {
                int tab = i;
                tabButtons[i] = UiFactory.CreateButton(bar, TabNames[i], () => ShowTab(tab));
            }

            Button hideButton = null;
            hideButton = UiFactory.CreateButton(bar, "Hide", () =>
            {
                panelsHidden = !panelsHidden;
                UiFactory.SetButtonLabel(hideButton, panelsHidden ? "Show" : "Hide");
                ShowTab(activeTab);
            });

            tabPanels = new GameObject[TabNames.Length];
            tabPanels[0] = BuildModellingPanel(root);
            tabPanels[1] = BuildTransformPanel(root);
            tabPanels[2] = BuildOptimisePanel(root);
            tabPanels[3] = BuildCutawayPanel(root);

            // Information panel on the right
            RectTransform info = UiFactory.CreatePanel(root, "Information", new Vector2(1f, 1f), new Vector2(-10f, -60f), 400f);
            infoPanel = info.gameObject;
            infoTitle = UiFactory.CreateText(info, "", 17, FontStyle.Bold);
            matrixCells = UiFactory.CreateMatrixGrid(info, out matrixGrid);
            infoText = UiFactory.CreateText(info, "", 15, FontStyle.Normal);

            // Bottom: hint text and buttons
            RectTransform hint = UiFactory.CreatePanel(root, "Hint", new Vector2(0f, 0f), new Vector2(10f, 10f), 560f);
            UiFactory.CreateText(hint,
                "Drag: orbit   Pinch / mouse wheel: zoom   Tap a part to select it, then drag to move,\n" +
                "pinch to scale, twist with two fingers to rotate.   Session: Bengaluru + Detroit", 14, FontStyle.Normal);

            RectTransform buttons = UiFactory.CreateRect("Bottom Buttons", root);
            buttons.anchorMin = new Vector2(1f, 0f);
            buttons.anchorMax = new Vector2(1f, 0f);
            buttons.pivot = new Vector2(1f, 0f);
            buttons.anchoredPosition = new Vector2(-10f, 10f);
            buttons.sizeDelta = new Vector2(420f, UiFactory.ControlHeight);
            HorizontalLayoutGroup buttonLayout = buttons.gameObject.AddComponent<HorizontalLayoutGroup>();
            buttonLayout.spacing = 6f;
            buttonLayout.childControlWidth = true;
            buttonLayout.childControlHeight = true;
            buttonLayout.childForceExpandWidth = true;
            buttonLayout.childForceExpandHeight = true;
            UiFactory.CreateButton(buttons, "Deselect", () => Select(null));
            UiFactory.CreateButton(buttons, "Reset part", ResetSelectedPart);
            UiFactory.CreateButton(buttons, "Reset view", ResetView);

            bengaluruLabel = CreateMarkerLabel(root, "Bengaluru team");
            detroitLabel = CreateMarkerLabel(root, "Detroit team");
        }

        Text CreateMarkerLabel(Transform root, string label)
        {
            Text text = UiFactory.CreateText(root, label, 16, FontStyle.Bold);
            text.rectTransform.anchorMin = Vector2.zero;
            text.rectTransform.anchorMax = Vector2.zero;
            text.rectTransform.pivot = new Vector2(0.5f, 0f);
            text.rectTransform.sizeDelta = new Vector2(180f, 24f);
            text.alignment = TextAnchor.LowerCenter;
            return text;
        }

        RectTransform CreateTabPanel(Transform root, string name)
        {
            return UiFactory.CreatePanel(root, name, new Vector2(0f, 1f), new Vector2(10f, -60f), 340f);
        }

        GameObject BuildModellingPanel(Transform root)
        {
            RectTransform panel = CreateTabPanel(root, "Modelling Panel");
            UiFactory.CreateText(panel,
                "Body, cabin, doors, mirrors: CSG union of boxes.\nTyres and rims: a 2D profile revolved around the axle " +
                "(rotational sweep), giving a boundary mesh.", 15, FontStyle.Normal);
            segmentsLabel = UiFactory.CreateText(panel, "", 16, FontStyle.Bold);
            UiFactory.CreateSlider(panel, 6f, 96f, rimSegments, true, value => SetRimSegments(Mathf.RoundToInt(value)));
            UiFactory.CreateText(panel,
                "Fewer segments = fewer triangles but a larger chordal error (gap to the true circle). Tap a part to see its matrix.",
                14, FontStyle.Italic);
            return panel.gameObject;
        }

        GameObject BuildTransformPanel(Transform root)
        {
            RectTransform panel = CreateTabPanel(root, "Transform Panel");
            UiFactory.CreateText(panel, "Wheel rim (front left): P' = M . P, distances in mm", 15, FontStyle.Bold);
            UiFactory.CreateButton(panel, "Case study: S(1.5), Rz(45), T(50 mm fwd)", () =>
            {
                lab.LoadPreset();
                lab.StartAnimation();
                ApplyTransformations();
            });

            scaleLabel = UiFactory.CreateText(panel, "", 15, FontStyle.Normal);
            UiFactory.CreateSlider(panel, 0.5f, 3f, stepScale, false, value => stepScale = Mathf.Round(value * 20f) / 20f);
            angleLabel = UiFactory.CreateText(panel, "", 15, FontStyle.Normal);
            UiFactory.CreateSlider(panel, -180f, 180f, stepAngle, true, value => stepAngle = value);
            moveLabel = UiFactory.CreateText(panel, "", 15, FontStyle.Normal);
            UiFactory.CreateSlider(panel, -200f, 200f, stepMove, true, value => stepMove = value);

            axisButton = UiFactory.CreateButton(panel, "", () => stepAxis = (stepAxis + 1) % 3);

            Transform row = UiFactory.CreateRow(panel);
            UiFactory.CreateButton(row, "+ Scale", () => AddStep(StepType.Scale));
            UiFactory.CreateButton(row, "+ Rotate", () => AddStep(StepType.Rotate));
            UiFactory.CreateButton(row, "+ Move", () => AddStep(StepType.Translate));

            row = UiFactory.CreateRow(panel);
            UiFactory.CreateButton(row, "+ Reflect", () => AddStep(StepType.Reflect));
            UiFactory.CreateButton(row, "+ Shear", () => AddStep(StepType.Shear));
            UiFactory.CreateButton(row, "Animate", () => lab.StartAnimation());

            row = UiFactory.CreateRow(panel);
            UiFactory.CreateButton(row, "Swap last 2", () => { lab.SwapLastTwo(); ApplyTransformations(); });
            UiFactory.CreateButton(row, "Undo", () =>
            {
                if (lab.steps.Count > 0)
                {
                    lab.steps.RemoveAt(lab.steps.Count - 1);
                }

                ApplyTransformations();
            });
            UiFactory.CreateButton(row, "Clear", () => { lab.steps.Clear(); ApplyTransformations(); });

            UiFactory.CreateToggle(panel, "Show wrong order (ghost rim)", showGhost, on =>
            {
                showGhost = on;
                ghostRim.gameObject.SetActive(on);
                ApplyTransformations();
            });
            return panel.gameObject;
        }

        GameObject BuildOptimisePanel(Transform root)
        {
            RectTransform panel = CreateTabPanel(root, "Optimise Panel");
            UiFactory.CreateToggle(panel, "Stereo: two eyes (VR dual displays)", stereo, on => stereo = on);
            UiFactory.CreateToggle(panel, "Back-face culling", backFaceCulling, SetBackFaceCulling);
            UiFactory.CreateToggle(panel, "Level of detail for wheels", lodWheels, on =>
            {
                lodWheels = on;

                if (!on)
                {
                    SetRimSegments(rimSegments);
                }
            });

            Transform row = UiFactory.CreateRow(panel);
            UiFactory.CreateButton(row, "Sit inside cabin", () => { insideCabin = true; Select(null); });
            UiFactory.CreateButton(row, "Orbit view", () => insideCabin = false);

            nearLabel = UiFactory.CreateText(panel, "", 15, FontStyle.Normal);
            UiFactory.CreateSlider(panel, 0.01f, 1f, nearPlane, false, value => nearPlane = value);
            UiFactory.CreateText(panel,
                "Unity already culls parts outside the view; the numbers on the right show how much each step saves.",
                14, FontStyle.Italic);
            return panel.gameObject;
        }

        GameObject BuildCutawayPanel(Transform root)
        {
            RectTransform panel = CreateTabPanel(root, "Cutaway Panel");
            UiFactory.CreateToggle(panel, "Cutaway on", cutaway, on => { cutaway = on; UpdateCutaway(); });
            cutAxisButton = UiFactory.CreateButton(panel, "", () => { cutAxis = (cutAxis + 1) % 3; UpdateCutaway(); });
            cutLabel = UiFactory.CreateText(panel, "", 15, FontStyle.Normal);
            UiFactory.CreateSlider(panel, -2.5f, 2.5f, cutPosition, false, value => { cutPosition = value; UpdateCutaway(); });
            UiFactory.CreateText(panel,
                "Red = inside surfaces exposed by the cut. Turn back-face culling on (Optimise tab) and the red insides vanish.",
                14, FontStyle.Italic);
            return panel.gameObject;
        }

        void ShowTab(int tab)
        {
            activeTab = tab;

            for (int i = 0; i < tabPanels.Length; i++)
            {
                tabPanels[i].SetActive(i == tab && !panelsHidden);
                UiFactory.SetButtonColor(tabButtons[i], i == tab ? UiFactory.ActiveColor : UiFactory.ButtonColor);
            }

            infoPanel.SetActive(!panelsHidden);
        }

        // ---------------- Information panel ----------------

        void RefreshInfo()
        {
            segmentsLabel.text = "Rim segments N = " + rimSegments;
            scaleLabel.text = "Scale factor: " + stepScale.ToString("0.00");
            angleLabel.text = "Rotation angle: " + stepAngle.ToString("0") + " deg";
            moveLabel.text = "Move distance: " + stepMove.ToString("0") + " mm";
            UiFactory.SetButtonLabel(axisButton, "Axis: " + AxisNames[stepAxis] + "  (tap to change)");
            nearLabel.text = "Near clipping plane: " + nearPlane.ToString("F2") + " m";
            cutLabel.text = "Plane position: " + "xyz"[cutAxis] + " = " + cutPosition.ToString("F2") + " m";
            UiFactory.SetButtonLabel(cutAxisButton, "Cut across: " + AxisNames[cutAxis] + "  (tap to change)");

            if (selected != null)
            {
                Transform part = selected.transform;
                infoTitle.text = "Selected: " + part.name + "\nModel matrix (local -> world), metres";
                matrixGrid.SetActive(true);
                UiFactory.ShowMatrix(matrixCells, part.localToWorldMatrix, "F3");
                infoText.text =
                    "Position: " + part.position.ToString("F3") + " m\n" +
                    "Rotation: " + part.eulerAngles.ToString("F1") + " deg\n" +
                    "Scale: " + part.lossyScale.ToString("F2") + "\n\n" +
                    "M = T x R x S. Drag to move, pinch to scale, twist to rotate. The change would be sent to the " +
                    "other site as this one matrix (64 bytes), not as the mesh.";
                return;
            }

            switch (activeTab)
            {
                case 0:
                    ShowModellingInfo();
                    break;
                case 1:
                    ShowTransformInfo();
                    break;
                case 2:
                    infoTitle.text = "Performance for the VR headset";
                    matrixGrid.SetActive(false);
                    infoText.text = statsText;
                    break;
                default:
                    ShowCutawayInfo();
                    break;
            }
        }

        void ShowModellingInfo()
        {
            infoTitle.text = "Geometric modelling";
            matrixGrid.SetActive(false);

            int carTriangles = 0;

            foreach (Renderer part in parts)
            {
                MeshFilter filter = part != null ? part.GetComponent<MeshFilter>() : null;

                if (filter != null && filter.sharedMesh != null && part.gameObject.activeInHierarchy)
                {
                    carTriangles += (int)(filter.sharedMesh.GetIndexCount(0) / 3);
                }
            }

            infoText.text =
                "CSG tree (U = union):\n" +
                "Car = Body U Cabin U Bonnet U Windscreen U 2 Doors U 2 Mirrors U 2 Lamps U Seats U 4 Wheels\n" +
                "Wheel = Tyre U Rim\n" +
                "Tyre = Revolve(tyre profile, N)\n" +
                "Rim = Revolve(barrel profile, N) U Revolve(hub profile, N) U 5 Spokes\n\n" +
                "B-rep check for a box: V - E + F = 8 - 12 + 6 = 2\n\n" +
                "Rim with N = " + rimSegments + ": " + studiedRim.TriangleCount + " triangles\n" +
                "Chordal error = R (1 - cos(pi / N)) = " + ChordalErrorMm(rimSegments).ToString("F2") + " mm (R = 235 mm)\n" +
                "Whole car: " + carTriangles + " triangles";
        }

        void ShowTransformInfo()
        {
            Matrix4x4 current = lab.CurrentMatrix();
            Matrix4x4 composite = lab.Composite();
            Vector3 check = composite.MultiplyPoint(new Vector3(100f, 0f, 0f));
            float difference = TransformLab.MaxDifference(composite, lab.UnityComposite());

            infoTitle.text = "Composite matrix M = Mn ... M2 . M1 (mm)" + (lab.Animating ? "  - animating" : "");
            matrixGrid.SetActive(true);
            UiFactory.ShowMatrix(matrixCells, current, "F3");

            string sequence = "";

            for (int i = 0; i < lab.steps.Count; i++)
            {
                sequence += "M" + (i + 1) + " = " + lab.steps[i].Describe() + "\n";
            }

            string ghost = "";

            if (showGhost)
            {
                Vector3 wrong = lab.WrongOrder().MultiplyPoint(new Vector3(100f, 0f, 0f));
                ghost = "\nGhost (pink) = same matrices in reverse order: (100, 0, 0) -> " + wrong.ToString("F2") + " mm";
            }

            infoText.text =
                (sequence.Length > 0 ? sequence : "No steps: M = identity\n") +
                "\nCheck point P = (100, 0, 0) mm -> P' = " + check.ToString("F2") + " mm\n" +
                "Unity's Matrix4x4.Scale / Rotate / Translate give the same M (largest difference " +
                difference.ToString("F5") + ")" + ghost;
        }

        void ShowCutawayInfo()
        {
            infoTitle.text = "Cutaway: clipping against a plane";
            matrixGrid.SetActive(false);
            char axis = "xyz"[cutAxis];

            infoText.text =
                (cutaway ? "Plane: " + axis + " = " + cutPosition.ToString("F2") + " m\n" : "Cutaway is off.\n") +
                "Each pixel of the car is tested against the plane: points with " + axis + " - " +
                cutPosition.ToString("F2") + " > 0 are discarded (clip() in the fragment shader).\n\n" +
                "This is the inside/outside half-space test that Sutherland-Hodgman applies to every polygon " +
                "vertex for each clipping plane; the view frustum is six such planes.";
        }
    }
}
