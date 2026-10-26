using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;

/// <summary>
/// Records every decision change and periodic need samples for all agents in the scene.
/// Drop this on an empty GameObject and press Play. Writes CSV files to RunData/ at the project root.
/// </summary>
public class DecisionLogger : MonoBehaviour
{
    private class AgentTrack
    {
        public AgentCore Core;
        public AgentMetabolism Metabolism;
        public UtilityAgent Utility;
        public string BrainName;
        public string LastAction = "";
        public int DecisionCount;
        public int InterruptCount;
    }

    [Header("Run Settings")]
    [Tooltip("Label written into every row. Use this to name the condition, e.g. full_utility or curves_only.")]
    public string ConditionLabel = "full";

    [Tooltip("Seconds of simulated time to record before the run stops automatically. 0 records until you stop Play.")]
    public float RunDuration = 300f;

    [Tooltip("Playback speed multiplier. 1 = real time. 10 means a 300-second run finishes in 30 real seconds. Recorded timestamps stay in simulated seconds either way.")]
    [Range(1f, 20f)] public float TimeScale = 1f;

    [Tooltip("Seconds between need-value samples written to the needs file.")]
    public float SampleInterval = 1f;

    [Header("Output")]
    [Tooltip("Folder relative to the project root. Created if missing.")]
    public string OutputFolder = "RunData";

    [Header("Live Readout (Read-Only)")]
    public float ElapsedTime;
    public int TotalDecisions;

    private readonly List<AgentTrack> _tracks = new List<AgentTrack>();
    private StreamWriter _decisionWriter;
    private StreamWriter _needWriter;
    private string _runId;
    private float _sampleTimer;
    private bool _finished;

    void Start()
    {
        _runId = System.DateTime.Now.ToString("yyyyMMdd_HHmmss");

        foreach (var core in FindObjectsByType<AgentCore>(FindObjectsSortMode.None))
        {
            var track = new AgentTrack
            {
                Core = core,
                Metabolism = core.GetComponent<AgentMetabolism>(),
                Utility = core.GetComponent<UtilityAgent>()
            };
            track.BrainName = track.Utility != null ? "Utility" : "Baseline";
            _tracks.Add(track);
        }

        if (_tracks.Count == 0)
        {
            Debug.LogError("[DecisionLogger] No AgentCore found in the scene. Nothing to record.");
            enabled = false;
            return;
        }

        string dir = Path.Combine(Application.dataPath, "..", OutputFolder);
        Directory.CreateDirectory(dir);

        _decisionWriter = new StreamWriter(Path.Combine(dir, $"decisions_{ConditionLabel}_{_runId}.csv"));
        _decisionWriter.WriteLine("run_id,condition,time_s,agent,brain,from_action,to_action,is_interrupt,hunger,energy,winning_score,inertia_applied");

        _needWriter = new StreamWriter(Path.Combine(dir, $"needs_{ConditionLabel}_{_runId}.csv"));
        _needWriter.WriteLine("run_id,condition,time_s,agent,brain,need,value");

        WriteConfigManifest(dir);

        Time.timeScale = TimeScale;

        Debug.Log($"[DecisionLogger] Recording {_tracks.Count} agent(s) at {TimeScale}x to {Path.GetFullPath(dir)}");
    }

    /// <summary>
    /// Records every parameter that shaped this run, so a CSV can always be traced
    /// back to the configuration that produced it.
    /// </summary>
    private void WriteConfigManifest(string dir)
    {
        var m = new StringBuilder();
        m.AppendLine($"run_id,{_runId}");
        m.AppendLine($"condition,{ConditionLabel}");
        m.AppendLine($"run_duration_s,{F(RunDuration)}");
        m.AppendLine($"time_scale,{F(TimeScale)}");
        m.AppendLine($"sample_interval_s,{F(SampleInterval)}");
        m.AppendLine($"unity_version,{Application.unityVersion}");
        m.AppendLine($"recorded_at,{System.DateTime.Now:yyyy-MM-dd HH:mm:ss}");

        foreach (var track in _tracks)
        {
            string a = track.Core.AgentLabel;
            m.AppendLine($"{a}.brain,{track.BrainName}");
            m.AppendLine($"{a}.decision_interval_s,{F(track.Core.DecisionInterval)}");
            m.AppendLine($"{a}.min_action_duration_s,{F(track.Core.MinActionDuration)}");

            if (track.Utility != null)
            {
                m.AppendLine($"{a}.activation_threshold,{F(track.Utility.ActivationThreshold)}");
                m.AppendLine($"{a}.commitment_bonus,{F(track.Utility.CommitmentBonus)}");
                foreach (var mapping in track.Utility.Curves)
                {
                    string need = mapping.Need != null ? mapping.Need.NeedName : "?";
                    string curve = mapping.Curve != null ? mapping.Curve.name : "none";
                    m.AppendLine($"{a}.curve.{need},{curve}");
                }
            }

            var baseline = track.Core.GetComponent<BaselineAgent>();
            if (baseline != null)
            {
                foreach (var rule in baseline.Rules)
                {
                    if (rule.Need == null) continue;
                    m.AppendLine($"{a}.threshold.{rule.Need.NeedName},{F(rule.Threshold)}");
                }
            }

            if (track.Metabolism != null)
            {
                foreach (var need in track.Metabolism.Needs)
                    m.AppendLine($"{a}.decay_rate.{need.Type.NeedName},{F(need.Type.BaseDecayRate)}");
            }
        }

        foreach (var obj in FindObjectsByType<SmartObject>(FindObjectsSortMode.None))
        {
            if (obj.Template == null) continue;
            foreach (var aff in obj.Template.Affordances)
            {
                m.AppendLine($"object.{obj.Template.ObjectName}.{aff.ActionName}.amount,{F(aff.Amount)}");
                m.AppendLine($"object.{obj.Template.ObjectName}.{aff.ActionName}.duration_s,{F(aff.Duration)}");
            }
        }

        File.WriteAllText(Path.Combine(dir, $"config_{ConditionLabel}_{_runId}.csv"), m.ToString());
    }

    void Update()
    {
        if (_finished) return;

        ElapsedTime += Time.deltaTime;

        foreach (var track in _tracks)
        {
            string current = track.Core.CurrentActionName;
            if (current == track.LastAction) continue;

            // Returning to idle is not a decision, but it does end the previous action.
            if (!string.IsNullOrEmpty(current))
            {
                bool isInterrupt = !string.IsNullOrEmpty(track.LastAction);
                track.DecisionCount++;
                if (isInterrupt) track.InterruptCount++;
                TotalDecisions++;
                WriteDecision(track, track.LastAction, current, isInterrupt);
            }

            track.LastAction = current;
        }

        _sampleTimer += Time.deltaTime;
        if (_sampleTimer >= SampleInterval)
        {
            _sampleTimer = 0f;
            WriteNeedSamples();
        }

        if (RunDuration > 0f && ElapsedTime >= RunDuration)
            Finish();
    }

    private void WriteDecision(AgentTrack track, string from, string to, bool isInterrupt)
    {
        float score = 0f;
        bool inertia = false;
        if (track.Utility != null)
        {
            foreach (var candidate in track.Utility.LastScores)
            {
                if (!candidate.Winner) continue;
                score = candidate.Score;
                inertia = candidate.InertiaApplied;
                break;
            }
        }

        _decisionWriter.WriteLine(string.Join(",",
            _runId,
            ConditionLabel,
            F(ElapsedTime),
            track.Core.AgentLabel,
            track.BrainName,
            string.IsNullOrEmpty(from) ? "idle" : from,
            to,
            isInterrupt ? "1" : "0",
            F(track.Metabolism.GetValue("Hunger")),
            F(track.Metabolism.GetValue("Energy")),
            track.Utility != null ? F(score) : "",
            track.Utility != null ? (inertia ? "1" : "0") : ""));
    }

    private void WriteNeedSamples()
    {
        foreach (var track in _tracks)
        {
            foreach (var need in track.Metabolism.Needs)
            {
                _needWriter.WriteLine(string.Join(",",
                    _runId,
                    ConditionLabel,
                    F(ElapsedTime),
                    track.Core.AgentLabel,
                    track.BrainName,
                    need.Type.NeedName,
                    F(need.CurrentValue)));
            }
        }
    }

    private void Finish()
    {
        if (_finished) return;
        _finished = true;

        var summary = new StringBuilder();
        summary.AppendLine($"[DecisionLogger] Run {_runId} finished after {ElapsedTime:F1}s");
        foreach (var track in _tracks)
        {
            float perMinute = ElapsedTime > 0f ? track.DecisionCount / (ElapsedTime / 60f) : 0f;
            summary.AppendLine(
                $"  {track.Core.AgentLabel} ({track.BrainName}): " +
                $"{track.DecisionCount} decisions, {track.InterruptCount} interrupts, " +
                $"{perMinute:F2} decisions/min");
        }
        Debug.Log(summary.ToString());

        Close();
    }

    private void Close()
    {
        Time.timeScale = 1f;
        if (_decisionWriter != null) { _decisionWriter.Flush(); _decisionWriter.Dispose(); _decisionWriter = null; }
        if (_needWriter != null) { _needWriter.Flush(); _needWriter.Dispose(); _needWriter = null; }
    }

    void OnDisable() { Finish(); }

    void OnApplicationQuit() { Finish(); }

    private static string F(float value) => value.ToString("F3", CultureInfo.InvariantCulture);
}
