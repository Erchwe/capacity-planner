from typing import List, Dict


BASE_ARRIVAL_RATE = 10  # requests per minute (unitless baseline)


def simulate_queue(
    traffic_curve: List[float],
    queue_capacity: int
) -> List[int]:
    """
    Simulate queue length over time for a single service.

    Args:
        traffic_curve: List of traffic load values per minute
        queue_capacity: Maximum queue capacity for the service

    Returns:
        List of queue lengths per minute
    """
    if queue_capacity <= 0:
        raise ValueError("queue_capacity must be positive")

    queue = 0
    queue_history: List[int] = []

    # Processing capacity: simplified as a fraction of queue capacity
    processing_capacity = max(1, queue_capacity // 10)

    for load in traffic_curve:
        incoming = int(load * BASE_ARRIVAL_RATE)
        processed = min(queue, processing_capacity)

        queue = queue + incoming - processed

        # Enforce hard queue cap
        queue = min(queue, queue_capacity)

        queue_history.append(queue)

    return queue_history


def summarize_queue(queue_history: List[int]) -> Dict[str, int]:
    """
    Summarize queue behavior.

    Returns:
        Dict with final and max queue length.
    """
    if not queue_history:
        return {"final": 0, "max": 0}

    return {
        "final": queue_history[-1],
        "max": max(queue_history)
    }
