from typing import List


def generate_traffic_curve(
    pattern: str,
    peak_multiplier: float,
    duration_minutes: int
) -> List[float]:
    """
    Generate a deterministic traffic load curve.

    Args:
        pattern: One of ["steady", "spike", "ramp"]
        peak_multiplier: Load multiplier at peak
        duration_minutes: Total simulation duration (1 step = 1 minute)

    Returns:
        List of traffic load values per minute.
    """
    if duration_minutes <= 0:
        raise ValueError("duration_minutes must be positive")

    baseline = 1.0
    curve: List[float] = []

    if pattern == "steady":
        curve = [baseline for _ in range(duration_minutes)]

    elif pattern == "spike":
        # Simple 3-phase spike: rise → peak → fall
        third = duration_minutes // 3

        for i in range(duration_minutes):
            if i < third:
                curve.append(baseline)
            elif i < 2 * third:
                curve.append(baseline * peak_multiplier)
            else:
                curve.append(baseline)

        # Handle short durations gracefully
        if not curve:
            curve = [baseline]

    elif pattern == "ramp":
        if duration_minutes == 1:
            curve = [baseline * peak_multiplier]
        else:
            for i in range(duration_minutes):
                ratio = i / (duration_minutes - 1)
                load = baseline + ratio * (peak_multiplier - baseline)
                curve.append(load)

    else:
        raise ValueError(f"Unsupported traffic pattern: {pattern}")

    return curve
