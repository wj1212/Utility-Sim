using UnityEngine;
using System.Collections.Generic;

public class AgentMetabolism : MonoBehaviour
{
    [System.Serializable]
    public class NeedState
    {
        public NeedType Type;
        public float CurrentValue;

        public NeedState(NeedType type)
        {
            Type = type;
            CurrentValue = 1f;
        }
    }

    public List<NeedState> Needs = new List<NeedState>();
    public List<NeedType> InitialNeedDefinitions;

    private float _logTimer = 0f;

    void Start()
    {
  
        Needs.Clear();

        foreach(var def in InitialNeedDefinitions)
        {
            if (def != null)
            {
                Needs.Add(new NeedState(def));
            }
        }
    }

    void Update()
    {
        foreach (var need in Needs)
        {
            float decay = need.Type.BaseDecayRate * Time.deltaTime;
            need.CurrentValue -= decay;
            need.CurrentValue = Mathf.Clamp01(need.CurrentValue);
        }

        _logTimer += Time.deltaTime;
        if (_logTimer >= 5f)
        {
            string status = "[Metabolism] ";
            foreach (var n in Needs) 
            {
                status += $"{n.Type.NeedName}: {n.CurrentValue:F2} | ";
            }
            Debug.Log(status);
            _logTimer = 0f;
        }
    }

    public void AddValue(string needName, float amount)
    {
        var need = Needs.Find(n => n.Type.NeedName == needName);
        if (need != null)
        {
            need.CurrentValue += amount;
            need.CurrentValue = Mathf.Clamp01(need.CurrentValue);
            Debug.Log($"<color=cyan>[Metabolism]</color> {needName} increased by {amount}. New Value: {need.CurrentValue}");
        }
        else
        {
            Debug.LogWarning($"[Metabolism] Cannot find need named: {needName}. Check your ScriptableObject naming!");
        }
    }
}