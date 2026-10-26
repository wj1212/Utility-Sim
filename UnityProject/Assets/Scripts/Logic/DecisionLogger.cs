using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;

/// <summary>
/// Records every decision change and periodic need samples for all agents in the scene.
///
/// Two ways to use it. Leave AutoStart on and press Play for a single recorded run, or
/// turn AutoStart off and let AblationRunner drive it, calling BeginRun and EndRun once
/// per condition so each condition lands in its own set of files.
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
    [Tooltip("Start recording as soon as Play begins. Turn this off when AblationRunner drives the logger.")]
    public bool AutoStart = true;

    [Tooltip("Label written into every row and used as part of the filename.")]
    public string ConditionLabel = "full";

    [Tooltip("Seconds of simulated time per run. 0 records until something else stops it.")]
    public float RunDuration = 300f;

    [Tooltip("Playback speed. Only applied when this component starts the run itself.")]
    [Range(1f, 20f)] public float TimeScale = 1f;

    [Tooltip("Seconds between need samples.")]
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
    private bool _running;
    private string _outputDir;
    private int _seed = -1;

    public bool IsRunning => _running;
    public string OutputDirectory => _outputDir;

    void Start()
    {
        Discover();
        if (_tracks.Count == 0)
        {
            Debug.LogError("[DecisionLogger] No AgentCore found in the scene. Nothing to record.");
            enabled = false;
            return;
        }

        if (AutoStart)
        {
            Time.timeScale = TimeScale;
            BeginRun(ConditionLabel, -1, null);
        }
    }

    private void Discover()
    {
        _tracks.Clear();
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

        _outputDir = Path.GetFullPath(Path.Combine(Application.dataPath, "..", OutputFolder));
        Directory.CreateDirectory(_outputDir);
    }

    /// <summary>
    /// Opens a fresh set of files and starts recording. Pass -1 for seed when the run is
    /// not seeded. extraConfig is appended verbatim to the manifest, one key,value per line.
    /// </summary>
    public void BeginRun(string label, int seed, string extraConfig)
    {
        if (_running) EndRun();
        if (_tracks.Count == 0) Discover();

        ConditionLabel = label;
        _runId = System.DateTime.Now.ToString("yyyyMMdd_HHmmss_fff");
        ElapsedTime = 0f;
        TotalDecisions = 0;
        _sampleTimer = 0f;

        foreach (var t in _tracks)
        {
            t.LastAction = t.Core.CurrentActionName;
            t.DecisionCount = 0;
            t.InterruptCount = 0;
        }

        _decisionWriter = new StreamWriter(Path.Combine(_outputDir, "decisions_" + label + "_" + _runId + ".csv"));
        _decisionWriter.WriteLine("run_id,condition,seed,time_s,agent,brain,from_action,to_action,is_interrupt," +
                                  "hunger,energy,winning_score,inertia_applied,abandoned_elapsed,abandoned_duration");

        _needWriter = new StreamWriter(Path.Combine(_outputDir, "needs_" + label + "_" + _runId + ".csv"));
        _needWriter.WriteLine("run_id,condition,seed,time_s,agent,brain,need,value");

        WriteConfigManifest(seed, extraConfig);
        _running = true;
    }

    /// <summary>Flushes and closes the current run, printing a short summary.</summary>
    public void EndRun()
    {
        if (!_running) return;
        _running = false;

        var summary = new StringBuilder();
        summary.AppendLine("[DecisionLogger] " + ConditionLabel + " finished after " + ElapsedTime.ToString("F1") + "s");
        foreach (var track in _tracks)
        {
            float perMinute = ElapsedTime > 0f ? track.DecisionCount / (ElapsedTime / 60f) : 0f;
            summary.AppendLine("  " + track.Core.AgentLabel + " (" + track.BrainName + "): " +
                               track.DecisionCount + " decisions, " +
                               track.InterruptCount + " interrupts, " +
                               perMinute.ToString("F2") + " decisions/min");
        }
        Debug.Log(summary.ToString());

        Close();
    }

    void Update()
    {
        if (!_running) return;

        ElapsedTime += Time.deltaTime;

        foreach (var track in _tracks)
        {
            string current = track.Core.CurrentActionName;
            if (current == track.LastAction) continue;

            // Returning to idle ends an action but is not itself a decision.
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

        if (RunDuration > 0f && ElapsedTime >= RunDuration) EndRun();
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

        // Only meaningful on an interrupt: how far through the abandoned action the agent got.
        string elapsed = isInterrupt ? F(track.Core.LastAbandonedElapsed) : "";
        string duration = isInterrupt ? F(track.Core.LastAbandonedDuration) : "";

        _decisionWriter.WriteLine(string.Join(",",
            _runId,
            ConditionLabel,
            _seed.ToString(CultureInfo.InvariantCulture),
            F(ElapsedTime),
            track.Core.AgentLabel,
            track.BrainName,
            string.IsNullOrEmpty(from) ? "idle" : from,
            to,
            isInterrupt ? "1" : "0",
            F(track.Metabolism.GetValue("Hunger")),
            F(track.Metabolism.GetValue("Energy")),
            track.Utility != null ? F(score) : "",
            track.Utility != null ? (inertia ? "1" : "0") : "",
            elapsed,
            duration));
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
                    _seed.ToString(CultureInfo.InvariantCulture),
                    F(ElapsedTime),
                    track.Core.AgentLabel,
                    track.BrainName,
                    need.Type.NeedName,
                    F(need.CurrentValue)));
            }
        }
    }

    /// <summary>
    /// Records every parameter that shaped this run, so a CSV can always be traced
    /// back to the configuration that produced it.
    /// </summary>
    private void WriteConfigManifest(int seed, string extraConfig)
    {
        _seed = seed;
        var m = new StringBuilder();
        m.AppendLine("run_id," + _runId);
        m.AppendLine("condition," + ConditionLabel);
        m.AppendLine("seed," + seed);
        m.AppendLine("run_duration_s," + F(RunDuration));
        m.AppendLine("time_scale," + F(Time.timeScale));
        m.AppendLine("sample_interval_s," + F(SampleInterval));
        m.AppendLine("unity_version," + Application.unityVersion);
        m.AppendLine("recorded_at," + System.DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss"));

        foreach (var track in _tracks)
        {
            string a = track.Core.AgentLabel;
            m.AppendLine(a + ".brain," + track.BrainName);
            m.AppendLine(a + ".decision_interval_s," + F(track.Core.DecisionInterval));
            m.AppendLine(a + ".min_action_duration_s," + F(track.Core.MinActionDuration));

            if (track.Utility != null)
            {
                m.AppendLine(a + ".activation_threshold," + F(track.Utility.ActivationThreshold));
                m.AppendLine(a + ".commitment_bonus," + F(track.Utility.CommitmentBonus));
                m.AppendLine(a + ".curve_count," + track.Utility.Curves.Count);
                foreach (var mapping in track.Utility.Curves)
                {
                    string need = mapping.Need != null ? mapping.Need.NeedName : "?";
                    string curve = mapping.Curve != null ? mapping.Curve.name : "none";
                    m.AppendLine(a + ".curve." + need + "," + curve);
                }
            }

            var baseline = track.Core.GetComponent<BaselineAgent>();
            if (baseline != null)
            {
                foreach (var rule in baseline.Rules)
                {
                    if (rule.Need == null) continue;
                    m.AppendLine(a + ".threshold." + rule.Need.NeedName + "," + F(rule.Threshold));
                }
            }

            if (track.Metabolism != null)
            {
                foreach (var need in track.Metabolism.Needs)
                {
                    m.AppendLine(a + ".decay_rate." + need.Type.NeedName + "," + F(need.Type.BaseDecayRate));
                    m.AppendLine(a + ".initial." + need.Type.NeedName + "," + F(need.CurrentValue));
                }
            }
        }

        foreach (var obj in FindObjectsByType<SmartObject>(FindObjectsSortMode.None))
        {
            if (obj.Template == null) continue;
            string on = obj.isActiveAndEnabled ? "1" : "0";
            m.AppendLine("object." + obj.Template.ObjectName + ".enabled," + on);
            foreach (var aff in obj.Template.Affordances)
            {
                m.AppendLine("object." + obj.Template.ObjectName + "." + aff.ActionName + ".amount," + F(aff.Amount));
                m.AppendLine("object." + obj.Template.ObjectName + "." + aff.ActionName + ".duration_s," + F(aff.Duration));
            }
        }

        if (!string.IsNullOrEmpty(extraConfig)) m.Append(extraConfig);

        File.WriteAllText(Path.Combine(_outputDir, "config_" + ConditionLabel + "_" + _runId + ".csv"), m.ToString());
    }

    private void Close()
    {
        if (_decisionWriter != null) { _decisionWriter.Flush(); _decisionWriter.Dispose(); _decisionWriter = null; }
        if (_needWriter != null) { _needWriter.Flush(); _needWriter.Dispose(); _needWriter = null; }
    }

    void OnDisable()
    {
        if (_running) EndRun();
        Time.timeScale = 1f;
    }

    void OnApplicationQuit()
    {
        if (_running) EndRun();
        Time.timeScale = 1f;
    }

    private static string F(float value) => value.ToString("F3", CultureInfo.InvariantCulture);
}
