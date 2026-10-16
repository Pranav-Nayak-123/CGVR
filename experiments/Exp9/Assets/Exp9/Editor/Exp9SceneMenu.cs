using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace CGVR.Exp9
{
    // Adds the menu item CGVR Lab > Exp 9 - Build Interactive Scene, which creates the scene objects in
    // the editor so they can be inspected in the Hierarchy and saved with the scene (File > Save)
    public static class Exp9SceneMenu
    {
        [MenuItem("CGVR Lab/Exp 9 - Build Interactive Scene")]
        static void BuildScene()
        {
            GameObject root = SceneBuilder.Build();
            Selection.activeGameObject = root;
            EditorSceneManager.MarkSceneDirty(root.scene);
        }
    }
}
