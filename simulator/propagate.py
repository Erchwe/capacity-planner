from typing import List


QUEUE_LATENCY_FACTOR_MS = 2  # ms added per queue unit


def compute_latency_series(
    base_latency_ms: int,
    queue_history: List[int]
) -> List[int]:
    """
    Compute latency over time based on queue pressure.

    Args:
        base_latency_ms: Baseline service latency
        queue_history: Queue length per minute

    Returns:
        List of latency values per minute (ms)
    """
    if base_latency_ms <= 0:
        raise ValueError("base_latency_ms must be positive")

    latency_series: List[int] = []

    for queue_len in queue_history:
        latency = base_latency_ms + QUEUE_LATENCY_FACTOR_MS * queue_len
        latency_series.append(int(latency))

    return latency_series


def summarize_latency(latency_series: List[int]) -> int:
    """
    Summarize latency behavior.

    Returns:
        Peak latency observed.
    """
    if not latency_series:
        return 0

    return max(latency_series)
