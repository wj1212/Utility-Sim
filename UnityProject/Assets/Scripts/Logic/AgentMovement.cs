using UnityEngine;

[RequireComponent(typeof(Rigidbody2D))]
public class AgentMovement : MonoBehaviour
{
    public float Speed = 3.0f;
    public float StopDistance = 1.2f; 

    private Rigidbody2D _rb;
    private Vector2 _targetPosition;
    private bool _isMoving = false;

    void Awake()
    {
        _rb = GetComponent<Rigidbody2D>();
    }

    public void MoveTo(Vector3 target)
    {
        _targetPosition = new Vector2(target.x, target.y);
        _isMoving = true;
    }

    void FixedUpdate()
    {
        if (!_isMoving) return;

        float distance = Vector2.Distance(_rb.position, _targetPosition);

        if (distance <= StopDistance)
        {
            _isMoving = false;
            _rb.linearVelocity = Vector2.zero;
            Debug.Log($"<color=white>[Movement]</color> Target reached. Remaining distance: {distance:F2}");
        }
        else
        {
            Vector2 direction = (_targetPosition - _rb.position).normalized;
            _rb.MovePosition(_rb.position + direction * Speed * Time.fixedDeltaTime);
        }
    }

    public bool IsArrived()
    {
        return !_isMoving;
    }
}