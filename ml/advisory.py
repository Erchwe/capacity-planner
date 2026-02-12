import math
from typing import Dict


def sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x))


def compute_service_risk_scores(
    service_metrics: Dict[str, Dict],
    base_services: Dict
) -> Dict[str, float]:
    """
    Compute deterministic graph-aware risk scores.
    """

    # Hyperparameters (fixed for reproducibility)
    W_QUEUE = 0.6
    W_LATENCY = 0.4

    local_risk = {}

    # Step 1: compute local risk
    for service, metrics in service_metrics.items():
        queue = metrics["queue"]
        latency = metrics["latency_ms"]

        queue_capacity = base_services["services"][service]["queue_capacity"]
        base_latency = base_services["services"][service]["base_latency_ms"]

        queue_ratio = queue / queue_capacity
        latency_ratio = latency / (base_latency + 1)

        score = (W_QUEUE * queue_ratio) + (W_LATENCY * latency_ratio)
        local_risk[service] = score

    # Step 2: propagate via dependency graph
    final_risk = {}

    for service, score in local_risk.items():
        propagated = score
        dependencies = base_services["services"][service].get("dependencies", {})

        for dep, dep_cfg in dependencies.items():
            weight = dep_cfg.get("weight", 1.0)
            upstream_score = local_risk.get(dep, 0)
            propagated += weight * upstream_score

        NORMALIZATION_CONSTANT = 5.0
        normalized = propagated / NORMALIZATION_CONSTANT
        final_risk[service] = sigmoid(normalized)

    return final_risk
