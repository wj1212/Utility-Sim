using UnityEngine;

[CreateAssetMenu(fileName = "NewCurve", menuName = "Sim/Response Curve")]
public class NewCurve : ScriptableObject
{
    [Tooltip("X-Axis: Input Need (0-1), Y-Axis: Utility Score (0-1).")]
    public AnimationCurve Curve;

    public float Evaluate(float input)
    {
        return Curve.Evaluate(Mathf.Clamp01(input));
    }
}