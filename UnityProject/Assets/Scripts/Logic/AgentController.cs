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

    [Header("Baseline Thresholds")]
    public float HungerThreshold = 0.3f;
    public float EnergyThreshold = 0.2f;

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

        if (hunger != null && hunger.CurrentValue < HungerThreshold)
        {
            PrepareAction("Hunger");
        }
        else if (energy != null && energy.CurrentValue < EnergyThreshold)
        {
            PrepareAction("Energy");
        }
    }

    private void PrepareAction(string needName)
    {
        _currentTarget = FindBestObject(needName);
        if (_currentTarget != null)
        {
            Debug.Log($"<color=yellow>[Decision]</color> {needName} is too low. Moving to {_currentTarget.name}");
            _movement.MoveTo(_currentTarget.transform.position);
            CurrentState = AgentState.Moving;
        }
    }

    private void StartInteraction()
    {
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
            .FirstOrDefault(obj => obj.Template.Affordances.Any(a => a.TargetNeed.NeedName == needName));
    }
}