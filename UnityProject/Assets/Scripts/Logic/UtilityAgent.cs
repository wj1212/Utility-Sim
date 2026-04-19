using System.Collections.Generic;
using UnityEngine;

public class UtilityAgent : MonoBehaviour, IAgentBrain
{
    [System.Serializable]
    public class NeedCurve
    {
        public NeedType Need;
        [Tooltip("X = current need value (0 critical, 1 satisfied). Y = desire to restore (0 none, 1 urgent).")]
        public ResponseCurve Curve;
    }

    [System.Serializable]
    public struct ScoredCandidate
    {
        public string ActionName;
        public string NeedName;
        public float NeedValue;
        public float BaseScore;
        public float Score;
        public bool InertiaApplied;
        public bool Winner;
    }

    [Header("Response Curves (per need)")]
    public List<NeedCurve> Curves = new List<NeedCurve>();

    [Header("Activation")]
    [Tooltip("Minimum utility score required to begin acting. Below this, stay idle.")]
    [Range(0f, 1f)] public float ActivationThreshold = 0.3f;

    [Header("Action Inertia")]
    [Tooltip("Bonus added to the score of the currently active action to discourage flip-flopping. 0 disables inertia.")]
    [Range(0f, 0.5f)] public float CommitmentBonus = 0.15f;

    [Header("Debug (Read-Only)")]
    public List<ScoredCandidate> LastScores = new List<ScoredCandidate>();

    public AgentDecision Decide(
        AgentMetabolism metabolism,
        SmartObject[] worldObjects,
        string currentActionName)
    {
        LastScores.Clear();
        int winnerIndex = -1;
        float bestScore = ActivationThreshold;
        AgentDecision best = AgentDecision.Idle;

        foreach (var obj in worldObjects)
        {
            if (obj.Template == null) continue;
            foreach (var aff in obj.Template.Affordances)
            {
                if (aff.TargetNeed == null) continue;
                float value = metabolism.GetValue(aff.TargetNeed.NeedName);
                float baseScore = EvaluateCurve(aff.TargetNeed, value);

                bool inertia = !string.IsNullOrEmpty(currentActionName) && aff.ActionName == currentActionName;
                float score = baseScore + (inertia ? CommitmentBonus : 0f);

                LastScores.Add(new ScoredCandidate
                {
                    ActionName = aff.ActionName,
                    NeedName = aff.TargetNeed.NeedName,
                    NeedValue = value,
                    BaseScore = baseScore,
                    Score = score,
                    InertiaApplied = inertia,
                    Winner = false
                });

                if (score > bestScore)
                {
                    bestScore = score;
                    winnerIndex = LastScores.Count - 1;
                    best = new AgentDecision
                    {
                        ShouldAct = true,
                        Target = obj,
                        ChosenAffordance = aff
                    };
                }
            }
        }

        if (winnerIndex >= 0)
        {
            var w = LastScores[winnerIndex];
            w.Winner = true;
            LastScores[winnerIndex] = w;
        }
        return best;
    }

    public float EvaluateCurve(NeedType need, float value)
    {
        foreach (var mapping in Curves)
        {
            if (mapping.Need == need && mapping.Curve != null)
                return mapping.Curve.Evaluate(value);
        }
        return 1f - value;
    }
}
