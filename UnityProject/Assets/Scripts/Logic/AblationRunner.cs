using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;

/// <summary>
/// Runs the four-condition ablation unattended.
///
/// The two mechanisms under study are the response curve and action inertia, and both
/// live inside the utility agent. The four conditions are therefore the 2x2 of
/// curve on/off by inertia on/off, all within the same scoring architecture. Turning the
/// curve "off" means clearing the curve list, which makes UtilityAgent fall back to a
/// linear need-to-desire mapping. The threshold agent runs alongside in every condition
/// and is recorded as an external reference point rather than as one of the four cells.
///
/// Each condition is repeated across several seeds. A seed fixes the starting need values,
/// which are shared by both agents so the comparison within a run is fair.
///
/// Attach to an empty GameObject, turn AutoStart off on the DecisionLogger, and press Play.
/// </summary>
public class AblationRunner : MonoBehaviour
{
    [System.Serializable]
    public class Condition
    {
        public string Name = "condition";
        [Tooltip("Off clears the curve list, so scoring falls back to a linear mapping.")]
        public bool UseCurves = true;
        [Range(0f, 0.5f)] public float CommitmentBonus = 0.2f;
    }

    [Header("Conditions (the 2x2)")]
    public List<Condition> Conditions = new List<Condition>
    {
        new Condition { Name = "linear_noinertia", UseCurves = false, CommitmentBonus = 0f   },
        new Condition { Name = "linear_inertia",   UseCurves = false, CommitmentBonus = 0.2f },
        new Condition { Name = "curve_noinertia",  UseCurves = true,  CommitmentBonus = 0f   },
        new Condition { Name = "curve_inertia",    UseCurves = true,  CommitmentBonus = 0.2f },
    };

    [Header("Repeats")]
    [Tooltip("How many seeded repeats to run per condition.")]
    public int SeedsPerCondition = 8;

    [Tooltip("First seed. Seeds run consecutively from here.")]
    public int FirstSeed = 1;

    [Header("Run Settings")]
    [Tooltip("Simulated seconds per run.")]
    public float SecondsPerRun = 300f;

    [Tooltip("Playback speed. 10 means a 300-second run takes 30 seconds of real time.")]
    [Range(1f, 20f)] public float TimeScale = 10f;

    [Tooltip("Starting need values are drawn uniformly from this range, same values for both agents.")]
    public Vector2 InitialNeedRange = new Vector2(0.30f, 1.0f);

    [Header("Progress (Read-Only)")]
    public string CurrentCondition = "";
    public int CurrentSeed;
    public int RunsDone;
    public int RunsTotal;

    private DecisionLogger _logger;
    private AgentCore[] _agents;
    private UtilityAgent _utility;
    private Vector3[] _startPositions;
    private List<UtilityAgent.NeedCurve> _originalCurves;
    private float _originalBonus;

    void Start()
    {
        _logger = FindFirstObjectByType<DecisionLogger>();
        if (_logger == null)
        {
            Debug.LogError("[AblationRunner] No DecisionLogger in the scene.");
            enabled = false;
            return;
        }
        if (_logger.AutoStart)
        {
            Debug.LogWarning("[AblationRunner] DecisionLogger.AutoStart is on. " +
                             "Turn it off so the runner controls recording.");
        }

        _agents = FindObjectsByType<AgentCore>(FindObjectsSortMode.None);
        if (_agents.Length == 0)
        {
            Debug.LogError("[AblationRunner] No agents in the scene.");
            enabled = false;
            return;
        }

        _startPositions = new Vector3[_agents.Length];
        for (int i = 0; i < _agents.Length; i++) _startPositions[i] = _agents[i].transform.position;

        _utility = FindFirstObjectByType<UtilityAgent>();
        if (_utility != null)
        {
            _originalCurves = new List<UtilityAgent.NeedCurve>(_utility.Curves);
            _originalBonus = _utility.CommitmentBonus;
        }

        RunsTotal = Conditions.Count * SeedsPerCondition;
        StartCoroutine(RunAll());
    }

    private IEnumerator RunAll()
    {
        // Wait one frame so every agent's Start has run. AgentMetabolism builds its need
        // list there and sets each value to 1, which would otherwise overwrite our seeded
        // starting values on the very first run.
        yield return null;

        Time.timeScale = TimeScale;
        _logger.RunDuration = SecondsPerRun;

        Debug.Log("[AblationRunner] Starting " + RunsTotal + " runs at " + TimeScale + "x. " +
                  "Estimated wall clock: " +
                  (RunsTotal * SecondsPerRun / TimeScale / 60f).ToString("F1") + " minutes.");

        foreach (var condition in Conditions)
        {
            ApplyCondition(condition);

            for (int i = 0; i < SeedsPerCondition; i++)
            {
                int seed = FirstSeed + i;
                CurrentCondition = condition.Name;
                CurrentSeed = seed;

                ResetWorld(seed);

                // Let the reset settle for a frame before recording starts.
                yield return null;

                _logger.BeginRun(condition.Name + "_s" + seed.ToString("D2"), seed, DescribeCondition(condition));

                while (_logger.IsRunning) yield return null;

                RunsDone++;
                Debug.Log("[AblationRunner] " + RunsDone + " / " + RunsTotal + " complete.");
            }
        }

        Restore();
        Time.timeScale = 1f;
        CurrentCondition = "done";
        Debug.Log("[AblationRunner] ALL RUNS COMPLETE. " + RunsDone + " runs written to " + _logger.OutputDirectory);
    }

    private void ApplyCondition(Condition condition)
    {
        if (_utility == null) return;

        _utility.Curves.Clear();
        if (condition.UseCurves && _originalCurves != null)
            _utility.Curves.AddRange(_originalCurves);

        _utility.CommitmentBonus = condition.CommitmentBonus;
    }

    /// <summary>
    /// Puts every agent back to its starting position with freshly seeded needs.
    /// Both agents receive the same values so the within-run comparison stays fair.
    /// </summary>
    private void ResetWorld(int seed)
    {
        Random.InitState(seed);

        // Draw one value per need name, shared across agents.
        var drawn = new Dictionary<string, float>();
        foreach (var agent in _agents)
        {
            var metabolism = agent.Metabolism;
            if (metabolism == null) continue;
            foreach (var need in metabolism.Needs)
            {
                string key = need.Type.NeedName;
                if (!drawn.ContainsKey(key))
                    drawn[key] = Random.Range(InitialNeedRange.x, InitialNeedRange.y);
            }
        }

        for (int i = 0; i < _agents.Length; i++)
        {
            var agent = _agents[i];
            agent.ResetState();

            var movement = agent.GetComponent<AgentMovement>();
            if (movement != null) movement.Teleport(_startPositions[i]);

            var metabolism = agent.Metabolism;
            if (metabolism == null) continue;
            foreach (var need in metabolism.Needs)
                need.CurrentValue = drawn[need.Type.NeedName];
        }
    }

    private string DescribeCondition(Condition condition)
    {
        var sb = new StringBuilder();
        sb.AppendLine("ablation.condition," + condition.Name);
        sb.AppendLine("ablation.use_curves," + (condition.UseCurves ? 1 : 0));
        sb.AppendLine("ablation.commitment_bonus," + condition.CommitmentBonus.ToString("F3"));
        sb.AppendLine("ablation.seeds_per_condition," + SeedsPerCondition);
        sb.AppendLine("ablation.initial_need_min," + InitialNeedRange.x.ToString("F3"));
        sb.AppendLine("ablation.initial_need_max," + InitialNeedRange.y.ToString("F3"));
        return sb.ToString();
    }

    private void Restore()
    {
        if (_utility == null || _originalCurves == null) return;
        _utility.Curves.Clear();
        _utility.Curves.AddRange(_originalCurves);
        _utility.CommitmentBonus = _originalBonus;
    }

    void OnDisable()
    {
        Restore();
        Time.timeScale = 1f;
    }
}
