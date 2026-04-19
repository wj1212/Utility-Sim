using UnityEditor;
using UnityEngine;

public static class ResponseCurveWizard
{
    private const string Folder = "Assets/Curves";

    [MenuItem("Sim/Create Preset Curves/Human-Like (Procrastinating)")]
    public static void CreateHumanLike()
    {
        EnsureFolder();
        Create("HungerCurve_HumanLike", MakeHumanLike());
        Create("EnergyCurve_HumanLike", MakeHumanLike());
        AssetDatabase.SaveAssets();
        EditorUtility.DisplayDialog("Preset Curves",
            "Created HungerCurve_HumanLike and EnergyCurve_HumanLike in Assets/Curves.\n\n" +
            "Drop them onto UtilityAgent's Curves list.", "OK");
    }

    [MenuItem("Sim/Create Preset Curves/Linear (Eager)")]
    public static void CreateLinear()
    {
        EnsureFolder();
        Create("Curve_Linear", AnimationCurve.Linear(0f, 1f, 1f, 0f));
        AssetDatabase.SaveAssets();
    }

    [MenuItem("Sim/Create Preset Curves/Late-Panic (Very Relaxed)")]
    public static void CreateLatePanic()
    {
        EnsureFolder();
        Create("Curve_LatePanic", MakeLatePanic());
        AssetDatabase.SaveAssets();
    }

    private static AnimationCurve MakeHumanLike()
    {
        // x = need value (0 critical → 1 satisfied)
        // y = desire to restore (0 none → 1 urgent)
        // Flat and low until need drops below ~0.5, then rises; spikes hard below 0.2.
        var c = new AnimationCurve(
            new Keyframe(0.00f, 1.00f),
            new Keyframe(0.20f, 0.85f),
            new Keyframe(0.50f, 0.35f),
            new Keyframe(0.75f, 0.10f),
            new Keyframe(1.00f, 0.00f)
        );
        for (int i = 0; i < c.length; i++) c.SmoothTangents(i, 0f);
        return c;
    }

    private static AnimationCurve MakeLatePanic()
    {
        // Almost doesn't care until it's desperate. Extreme procrastinator.
        var c = new AnimationCurve(
            new Keyframe(0.00f, 1.00f),
            new Keyframe(0.15f, 0.80f),
            new Keyframe(0.30f, 0.35f),
            new Keyframe(0.60f, 0.05f),
            new Keyframe(1.00f, 0.00f)
        );
        for (int i = 0; i < c.length; i++) c.SmoothTangents(i, 0f);
        return c;
    }

    private static void Create(string name, AnimationCurve curve)
    {
        var asset = ScriptableObject.CreateInstance<ResponseCurve>();
        asset.Curve = curve;
        string path = AssetDatabase.GenerateUniqueAssetPath($"{Folder}/{name}.asset");
        AssetDatabase.CreateAsset(asset, path);
        Debug.Log($"Created {path}");
    }

    private static void EnsureFolder()
    {
        if (!AssetDatabase.IsValidFolder(Folder))
            AssetDatabase.CreateFolder("Assets", "Curves");
    }
}
