using UnityEngine;
using System.Linq;

public class AgentController : MonoBehaviour
{
    public enum AgentState { Idle, Moving, Interacting }

    [Header("Current Status")]
    public AgentState CurrentState = AgentState.Idle;
    public string CurrentActionName;

    private AgentMetabolism _metabolism;
    private AgentMovement _movement;
    private SmartObject _currentTarget;
    private float _interactionTimer = 0f;

    [Header("Brain Configurations (Curves)")]
    public ResponseCurve HungerBrain;
    public ResponseCurve EnergyBrain;

    [Range(0, 1)] public float ActivationScore = 0.5f; 

    void Start()
    {
        _metabolism = GetComponent<AgentMetabolism>();
        _movement = GetComponent<AgentMovement>();
    }

    void Update()
    {
        switch (CurrentState)
        {
            case AgentState.Idle:
                CheckNeeds();
                break;

            case AgentState.Moving:
                if (_movement.IsArrived())
                {
                    StartInteraction();
                }
                break;

            case AgentState.Interacting:
                HandleInteraction();
                break;
        }
    }

    private void CheckNeeds()
    {
        var hunger = _metabolism.Needs.Find(n => n.Type.NeedName == "Hunger");
        var energy = _metabolism.Needs.Find(n => n.Type.NeedName == "Energy");

        
        if (hunger != null && HungerBrain != null)
        {
            float hungerDesire = HungerBrain.Evaluate(hunger.CurrentValue);
            if (hungerDesire > ActivationScore)
            {
                PrepareAction("Hunger");
                return; 
            }
        }

        if (energy != null && EnergyBrain != null)
        {
            float energyDesire = EnergyBrain.Evaluate(energy.CurrentValue);
            if (energyDesire > ActivationScore)
            {
                PrepareAction("Energy");
            }
        }
    }

    private void PrepareAction(string needName)
    {
        _currentTarget = FindBestObject(needName);
        if (_currentTarget != null)
        {
            Debug.Log($"<color=yellow>[Decision]</color> Utility for {needName} is high. Moving to {_currentTarget.name}");
            _movement.MoveTo(_currentTarget.transform.position);
            CurrentState = AgentState.Moving;
        }
    }

    private void StartInteraction()
    {
        if (_currentTarget == null) return;
        CurrentState = AgentState.Interacting;
        var affordance = _currentTarget.Template.Affordances[0];
        _interactionTimer = affordance.Duration;
        CurrentActionName = affordance.ActionName;
        Debug.Log($"<color=green>[Action]</color> Arrived at {_currentTarget.name}. Starting to {CurrentActionName} for {_interactionTimer}s.");
    }

    private void HandleInteraction()
    {
        if (_currentTarget == null) return;

        var affordance = _currentTarget.Template.Affordances[0];
        float tickAmount = (affordance.Amount / affordance.Duration) * Time.deltaTime;
        
        _metabolism.AddValue(affordance.TargetNeed.NeedName, tickAmount);
        _interactionTimer -= Time.deltaTime;

        if (_interactionTimer <= 0)
        {
            Debug.Log($"<color=cyan>[Success]</color> Finished {affordance.ActionName}. Interaction complete.");
            CurrentState = AgentState.Idle;
            _currentTarget = null;
        }
    }

    private SmartObject FindBestObject(string needName)
    {
        return FindObjectsByType<SmartObject>(FindObjectsSortMode.None)
            .FirstOrDefault(obj => obj.Template != null && obj.Template.Affordances.Any(a => a.TargetNeed.NeedName == needName));
    }
}