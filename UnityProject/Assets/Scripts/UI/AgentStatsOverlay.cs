using System.Linq;
using UnityEngine;

public class AgentStatsOverlay : MonoBehaviour
{
    [Header("Layout")]
    public int PanelWidth = 310;
    public int Padding = 12;

    [Header("Colors")]
    public Color BaselineAccent = new Color(0.90f, 0.35f, 0.35f);
    public Color UtilityAccent = new Color(0.35f, 0.70f, 0.90f);
    public Color PanelBg = new Color(0.08f, 0.08f, 0.10f, 0.88f);
    public Color BarBg = new Color(0.18f, 0.18f, 0.20f, 1f);
    public Color TextDim = new Color(0.75f, 0.75f, 0.78f, 1f);
    public Color Winner = new Color(1f, 0.85f, 0.25f, 1f);

    private GUIStyle _title, _sub, _body, _bodyDim, _score, _scoreWin;
    private Texture2D _flat;

    void OnGUI()
    {
        EnsureStyles();

        var cores = FindObjectsByType<AgentCore>(FindObjectsSortMode.None)
            .OrderBy(a => a.AgentLabel)
            .ToArray();

        float y = Padding;
        foreach (var core in cores)
        {
            y += DrawAgent(core, Padding, y) + Padding;
        }
    }

    private float DrawAgent(AgentCore core, float x, float y)
    {
        var utility = core.GetComponent<UtilityAgent>();
        Color accent = utility != null ? UtilityAccent : BaselineAccent;

        // measure height
        int needCount = core.Metabolism != null ? core.Metabolism.Needs.Count : 0;
        int scoreCount = utility != null ? utility.LastScores.Count : 0;
        float height = 54f + needCount * 42f + (utility != null ? 24f + scoreCount * 20f + 8f : 0f);

        // panel background
        DrawRect(new Rect(x, y, PanelWidth, height), PanelBg);
        // accent strip on left
        DrawRect(new Rect(x, y, 4f, height), accent);
        // title bar
        DrawRect(new Rect(x + 4, y, PanelWidth - 4, 26f), new Color(accent.r, accent.g, accent.b, 0.25f));
        GUI.Label(new Rect(x + 14, y + 4, PanelWidth - 20, 22f),
            $"{core.AgentLabel}  ·  {(utility != null ? "UTILITY" : "BASELINE")}",
            _title);

        float cy = y + 30f;
        string action = string.IsNullOrEmpty(core.CurrentActionName) ? "—" : core.CurrentActionName;
        GUI.Label(new Rect(x + 14, cy, PanelWidth - 20, 18f),
            $"{core.CurrentState}  ·  {action}", _sub);
        cy += 22f;

        if (core.Metabolism != null)
        {
            foreach (var need in core.Metabolism.Needs)
            {
                DrawNeedRow(x + 14, cy, PanelWidth - 28, need, utility);
                cy += 42f;
            }
        }

        if (utility != null)
        {
            DrawRect(new Rect(x + 14, cy + 4, PanelWidth - 28, 1f), new Color(1, 1, 1, 0.1f));
            cy += 10f;
            GUI.Label(new Rect(x + 14, cy, PanelWidth - 28, 18f), "LAST DECISION", _bodyDim);
            cy += 18f;
            foreach (var c in utility.LastScores)
            {
                DrawScoreRow(x + 14, cy, PanelWidth - 28, c);
                cy += 20f;
            }
        }

        return height;
    }

    private void DrawNeedRow(float x, float y, float w, AgentMetabolism.NeedState need, UtilityAgent utility)
    {
        GUI.Label(new Rect(x, y, w, 16f), need.Type.NeedName, _body);

        string rightText = utility != null
            ? $"{need.CurrentValue:F2}   desire {utility.EvaluateCurve(need.Type, need.CurrentValue):F2}"
            : $"{need.CurrentValue:F2}";
        var rightStyle = new GUIStyle(_bodyDim) { alignment = TextAnchor.UpperRight };
        GUI.Label(new Rect(x, y, w, 16f), rightText, rightStyle);

        // bar
        var bg = new Rect(x, y + 18f, w, 14f);
        DrawRect(bg, BarBg);
        float v = Mathf.Clamp01(need.CurrentValue);
        var fgColor = need.Type.VisualColor;
        // dim as value drops
        var barColor = Color.Lerp(new Color(0.9f, 0.3f, 0.3f, 1f), fgColor, v);
        DrawRect(new Rect(bg.x, bg.y, bg.width * v, bg.height), barColor);
    }

    private void DrawScoreRow(float x, float y, float w, UtilityAgent.ScoredCandidate c)
    {
        var style = c.Winner ? _scoreWin : _score;
        string marker = c.Winner ? "★" : "·";
        string inertia = c.InertiaApplied ? $"  (+{(c.Score - c.BaseScore):F2} inertia)" : "";
        GUI.Label(new Rect(x, y, w * 0.55f, 18f),
            $"{marker} {c.ActionName}", style);
        var rightStyle = new GUIStyle(style) { alignment = TextAnchor.UpperRight };
        GUI.Label(new Rect(x, y, w, 18f),
            $"{c.Score:F2}{inertia}", rightStyle);
    }

    private void DrawRect(Rect rect, Color color)
    {
        var prev = GUI.color;
        GUI.color = color;
        GUI.DrawTexture(rect, _flat);
        GUI.color = prev;
    }

    private void EnsureStyles()
    {
        if (_flat == null) _flat = Texture2D.whiteTexture;
        if (_title == null)
            _title = new GUIStyle { fontSize = 14, fontStyle = FontStyle.Bold, normal = { textColor = Color.white } };
        if (_sub == null)
            _sub = new GUIStyle { fontSize = 12, normal = { textColor = TextDim } };
        if (_body == null)
            _body = new GUIStyle { fontSize = 13, fontStyle = FontStyle.Bold, normal = { textColor = Color.white } };
        if (_bodyDim == null)
            _bodyDim = new GUIStyle { fontSize = 11, normal = { textColor = TextDim } };
        if (_score == null)
            _score = new GUIStyle { fontSize = 12, normal = { textColor = TextDim } };
        if (_scoreWin == null)
            _scoreWin = new GUIStyle { fontSize = 12, fontStyle = FontStyle.Bold, normal = { textColor = Winner } };
    }
}
