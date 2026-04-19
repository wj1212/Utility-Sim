public struct AgentDecision
{
    public bool ShouldAct;
    public SmartObject Target;
    public Affordance ChosenAffordance;

    public static AgentDecision Idle => new AgentDecision { ShouldAct = false };
}

public interface IAgentBrain
{
    AgentDecision Decide(
        AgentMetabolism metabolism,
        SmartObject[] worldObjects,
        string currentActionName);
}
