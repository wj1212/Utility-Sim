using UnityEngine;
using System.Collections.Generic;

[System.Serializable]
public struct Affordance
{
    public string ActionName;
    public NeedType TargetNeed;
    public float Amount;
    public float Duration;
}

[CreateAssetMenu(fileName = "NewObjectData", menuName = "Sim/Object Data")]
public class SmartObjectData : ScriptableObject
{
    public string ObjectName;
    public List<Affordance> Affordances;
}