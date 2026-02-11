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

from typing import Dict


def propagate_dependency_latency(
    local_latencies: Dict[str, int],
    service_dependencies: Dict[str, Dict[str, float]]
) -> Dict[str, int]:
    """
    Propagate latency across service dependencies (1-hop).

    Args:
        local_latencies: {service: latency_ms}
        service_dependencies: {
            service: {dependency: weight}
        }

    Returns:
        Dict of effective latency per service.
    """
    effective_latencies = {}

    for service, base_latency in local_latencies.items():
        propagated = base_latency
        dependencies = service_dependencies.get(service, {})

        for dep, dep_cfg in dependencies.items():
            weight = dep_cfg.get("weight", 1.0)
            upstream_latency = local_latencies.get(dep, 0)
            propagated += int(weight * upstream_latency)

        effective_latencies[service] = propagated

    return effective_latencies
