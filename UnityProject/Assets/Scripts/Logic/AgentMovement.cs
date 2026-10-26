using UnityEngine;

[RequireComponent(typeof(Rigidbody2D))]
public class AgentMovement : MonoBehaviour
{
    [Header("Movement")]
    public float Speed = 3.0f;
    public float StopDistance = 1.2f;

    [Header("Agent Avoidance")]
    [Tooltip("Distance at which other agents push this one aside.")]
    public float AvoidRadius = 1.0f;
    [Tooltip("How strongly other agents deflect this one. 0 = no avoidance.")]
    [Range(0f, 2f)] public float AvoidStrength = 0.7f;

    private Rigidbody2D _rb;
    private Vector2 _targetPosition;
    private bool _isMoving;

    private static readonly Collider2D[] _overlapBuffer = new Collider2D[8];

    void Awake()
    {
        _rb = GetComponent<Rigidbody2D>();
    }

    public void MoveTo(Vector3 target)
    {
        _targetPosition = new Vector2(target.x, target.y);
        _isMoving = true;
    }

    public bool IsArrived() => !_isMoving;

    /// <summary>Halts movement immediately. Used when resetting between runs.</summary>
    public void Stop()
    {
        _isMoving = false;
        if (_rb != null) _rb.linearVelocity = Vector2.zero;
    }

    /// <summary>Teleports the agent and clears any movement in progress.</summary>
    public void Teleport(Vector2 position)
    {
        Stop();
        if (_rb != null) _rb.position = position;
        transform.position = new Vector3(position.x, position.y, transform.position.z);
    }

    void FixedUpdate()
    {
        if (!_isMoving) return;

        float distance = Vector2.Distance(_rb.position, _targetPosition);
        if (distance <= StopDistance)
        {
            _isMoving = false;
            _rb.linearVelocity = Vector2.zero;
            return;
        }

        Vector2 seek = (_targetPosition - _rb.position).normalized;
        Vector2 avoid = ComputeAvoidance();
        Vector2 dir = (seek + avoid * AvoidStrength).normalized;

        _rb.MovePosition(_rb.position + dir * Speed * Time.fixedDeltaTime);
    }

    private Vector2 ComputeAvoidance()
    {
        Vector2 pushback = Vector2.zero;
        int count = Physics2D.OverlapCircleNonAlloc(_rb.position, AvoidRadius, _overlapBuffer);
        for (int i = 0; i < count; i++)
        {
            var other = _overlapBuffer[i];
            if (other == null) continue;
            if (other.attachedRigidbody == _rb) continue;
            if (other.GetComponent<AgentCore>() == null) continue;

            Vector2 away = _rb.position - (Vector2)other.transform.position;
            float mag = away.magnitude;
            if (mag < 0.001f) continue;
            pushback += away.normalized * Mathf.Clamp01(1f - mag / AvoidRadius);
        }
        return pushback;
    }
}
