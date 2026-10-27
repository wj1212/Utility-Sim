using UnityEngine;

/// <summary>
/// Takes a smart object away for a window in the middle of a run, then gives it back.
///
/// With every resource permanently available the two needs never both reach the
/// intervention point at once, so the part of the utility agent that ranks competing
/// options never has to run. Removing one resource for a while lets the need it serves
/// fall far below the threshold, so when it returns the agent faces two urgent needs
/// at the same time. That is the condition the response curve is actually for.
///
/// Disabling the GameObject is enough: AgentCore rescans the world each decision cycle
/// and simply stops seeing the object, and an agent mid-interaction drops the action
/// because its target becomes null.
/// </summary>
public class ResourceOutage : MonoBehaviour
{
    [Tooltip("Which object disappears. Usually the fridge.")]
    public SmartObject Target;

    [Tooltip("Simulated seconds into the run when the object is removed.")]
    public float StartSeconds = 100f;

    [Tooltip("Simulated seconds into the run when it comes back.")]
    public float EndSeconds = 160f;

    [Tooltip("Run the outage on its own timer as soon as Play starts. Leave off when AblationRunner drives it.")]
    public bool AutoStart = false;

    [Header("Live Readout (Read-Only)")]
    public float Elapsed;
    public bool TargetRemoved;

    private bool _active;

    public bool IsConfigured => Target != null;

    void Start()
    {
        if (AutoStart) BeginWindow();
    }

    /// <summary>Restarts the outage clock and makes the target available again.</summary>
    public void BeginWindow()
    {
        Elapsed = 0f;
        _active = true;
        SetRemoved(false);
    }

    /// <summary>Stops the outage and leaves the target available.</summary>
    public void Clear()
    {
        _active = false;
        Elapsed = 0f;
        SetRemoved(false);
    }

    void Update()
    {
        if (!_active || Target == null) return;

        Elapsed += Time.deltaTime;

        bool shouldBeRemoved = Elapsed >= StartSeconds && Elapsed < EndSeconds;
        if (shouldBeRemoved != TargetRemoved) SetRemoved(shouldBeRemoved);
    }

    private void SetRemoved(bool removed)
    {
        TargetRemoved = removed;
        if (Target != null) Target.gameObject.SetActive(!removed);
    }

    void OnDisable()
    {
        // Never leave the scene with a resource missing.
        if (Target != null) Target.gameObject.SetActive(true);
    }
}
