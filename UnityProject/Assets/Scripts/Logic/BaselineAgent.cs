using System.Collections.Generic;
using UnityEngine;

public class BaselineAgent : MonoBehaviour, IAgentBrain
{
    [System.Serializable]
    public class NeedRule
    {
        public NeedType Need;
        [Range(0f, 1f)] public float Threshold = 0.3f;
    }

    [Tooltip("Rigid priority order. The agent acts on the first rule whose need is below its threshold.")]
    public List<NeedRule> Rules = new List<NeedRule>();

    public AgentDecision Decide(
        AgentMetabolism metabolism,
        SmartObject[] worldObjects,
        string currentActionName)
    {
        foreach (var rule in Rules)
        {
            if (rule.Need == null) continue;
            float value = metabolism.GetValue(rule.Need.NeedName);
            if (value < rule.Threshold)
            {
                if (TryFindAffordance(rule.Need.NeedName, worldObjects, out var target, out var aff))
                {
                    return new AgentDecision
                    {
                        ShouldAct = true,
                        Target = target,
                        ChosenAffordance = aff
                    };
                }
            }
        }
        return AgentDecision.Idle;
    }

    private static bool TryFindAffordance(
        string needName,
        SmartObject[] worldObjects,
        out SmartObject target,
        out Affordance affordance)
    {
        foreach (var obj in worldObjects)
        {
            if (obj.Template == null) continue;
            foreach (var aff in obj.Template.Affordances)
            {
                if (aff.TargetNeed != null && aff.TargetNeed.NeedName == needName)
                {
                    target = obj;
                    affordance = aff;
                    return true;
                }
            }
        }
        target = null;
        affordance = default;
        return false;
    }
}
