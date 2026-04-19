using UnityEngine;

[RequireComponent(typeof(AgentMetabolism))]
[RequireComponent(typeof(AgentMovement))]
public class AgentCore : MonoBehaviour
{
    public enum AgentState { Idle, Moving, Interacting }

    [Header("Display")]
    public string AgentLabel = "Agent";

    [Header("Decision Cadence")]
    [Tooltip("Seconds between brain evaluations.")]
    public float DecisionInterval = 0.5f;

    [Header("Approach")]
    [Tooltip("Sideways offset relative to the approach direction. Negative = left of approach, positive = right. Keeps two agents on opposite sides of a shared target regardless of where it is in the room.")]
    public float SideOffset = 0f;

    [Header("Commitment")]
    [Tooltip("Minimum seconds an action must run before the brain is allowed to interrupt it.")]
    public float MinActionDuration = 1.5f;

    [Header("Current Status (Read-Only)")]
    public AgentState CurrentState = AgentState.Idle;
    public string CurrentActionName = "";

    private AgentMetabolism _metabolism;
    private AgentMovement _movement;
    private IAgentBrain _brain;
    private SmartObject _currentTarget;
    private Affordance _currentAffordance;
    private float _interactionTimer;
    private float _decisionTimer;
    private float _actionElapsed;

    public AgentMetabolism Metabolism => _metabolism;

    void Start()
    {
        _metabolism = GetComponent<AgentMetabolism>();
        _movement = GetComponent<AgentMovement>();
        _brain = GetComponent<IAgentBrain>();
        if (_brain == null)
            Debug.LogError($"[{AgentLabel}] No IAgentBrain component found. Add BaselineAgent or UtilityAgent.");
    }

    void Update()
    {
        switch (CurrentState)
        {
            case AgentState.Idle: TickIdle(); break;
            case AgentState.Moving: TickMoving(); break;
            case AgentState.Interacting: TickInteracting(); break;
        }
    }

    private void TickIdle()
    {
        _decisionTimer -= Time.deltaTime;
        if (_decisionTimer > 0f) return;
        _decisionTimer = DecisionInterval;

        if (_brain == null) return;
        var world = FindObjectsByType<SmartObject>(FindObjectsSortMode.None);
        var decision = _brain.Decide(_metabolism, world, CurrentActionName);

        if (decision.ShouldAct && decision.Target != null)
        {
            BeginPursuit(decision);
        }
        else
        {
            CurrentActionName = "";
        }
    }

    private void TickMoving()
    {
        if (_movement.IsArrived())
        {
            _interactionTimer = _currentAffordance.Duration;
            _actionElapsed = 0f;
            CurrentState = AgentState.Interacting;
            Debug.Log($"[{AgentLabel}] Started {CurrentActionName} for {_interactionTimer:F1}s");
        }
    }

    private void TickInteracting()
    {
        if (_currentTarget == null) { EndInteraction(); return; }

        float tick = (_currentAffordance.Amount / _currentAffordance.Duration) * Time.deltaTime;
        _metabolism.AddValue(_currentAffordance.TargetNeed.NeedName, tick);
        _interactionTimer -= Time.deltaTime;
        _actionElapsed += Time.deltaTime;

        _decisionTimer -= Time.deltaTime;
        if (_decisionTimer <= 0f && _actionElapsed >= MinActionDuration)
        {
            _decisionTimer = DecisionInterval;
            var world = FindObjectsByType<SmartObject>(FindObjectsSortMode.None);
            var decision = _brain.Decide(_metabolism, world, CurrentActionName);
            if (decision.ShouldAct
                && decision.Target != null
                && decision.ChosenAffordance.ActionName != CurrentActionName)
            {
                Debug.Log($"[{AgentLabel}] INTERRUPT {CurrentActionName} -> {decision.ChosenAffordance.ActionName}");
                BeginPursuit(decision);
                return;
            }
        }

        if (_interactionTimer <= 0f)
        {
            Debug.Log($"[{AgentLabel}] Finished {CurrentActionName}");
            EndInteraction();
        }
    }

    private void BeginPursuit(AgentDecision decision)
    {
        _currentTarget = decision.Target;
        _currentAffordance = decision.ChosenAffordance;
        CurrentActionName = decision.ChosenAffordance.ActionName;
        Vector2 toTarget = (Vector2)_currentTarget.transform.position - (Vector2)transform.position;
        Vector2 approachDir = toTarget.sqrMagnitude > 0.0001f ? toTarget.normalized : Vector2.right;
        Vector2 sideways = new Vector2(approachDir.y, -approachDir.x); // 90° clockwise = "right of approach"
        Vector3 dest = _currentTarget.transform.position + (Vector3)(sideways * SideOffset);
        _movement.MoveTo(dest);
        CurrentState = AgentState.Moving;
        Debug.Log($"[{AgentLabel}] Decide -> {CurrentActionName} @ {_currentTarget.name}");
    }

    private void EndInteraction()
    {
        CurrentState = AgentState.Idle;
        _currentTarget = null;
        CurrentActionName = "";
        _decisionTimer = 0f;
    }
}
