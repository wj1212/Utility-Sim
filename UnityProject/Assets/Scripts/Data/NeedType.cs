using UnityEngine;

[CreateAssetMenu(fileName = "NewNeed", menuName = "Sim/Need Type")]
public class NeedType : ScriptableObject
{
    public string Name;
    public Color VisualColor = Color.white;
    public float BaseDecayRate = 0.01f;
}