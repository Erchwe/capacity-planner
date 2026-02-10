import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import json
import os
from datetime import datetime

import yaml
from jsonschema import validate, ValidationError

from simulator.traffic import generate_traffic_curve
from simulator.queue import simulate_queue, summarize_queue
from simulator.propagate import compute_latency_series, summarize_latency



BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "configs"
RUNS_DIR = BASE_DIR / "runs"


def load_base_services():
    with open(CONFIG_DIR / "base_services.yaml", "r") as f:
        return yaml.safe_load(f)


def load_scenario_config():
    """
    For Day 1, we hardcode a sample scenario.
    Later, this will be provided by the dashboard.
    """
    return {
        "traffic": {
            "pattern": "spike",
            "peak_multiplier": 3.0,
            "duration_minutes": 20
        },
        "service_overrides": {
            "auth": {
                "base_latency_ms": 120
            }
        },
        "scaling_policy": {
            "aggressiveness": "medium",
            "cooldown_minutes": 10,
            "risk_tolerance": "conservative"
        }
    }


def validate_scenario(scenario):
    with open(CONFIG_DIR / "scenario_schema.json", "r") as f:
        schema = json.load(f)

    try:
        validate(instance=scenario, schema=schema)
    except ValidationError as e:
        raise RuntimeError(f"Scenario validation failed: {e.message}")


def run_simulation(base_services, scenario):
    """
    Run deterministic service-level simulation.
    """
    traffic_cfg = scenario["traffic"]

    traffic_curve = generate_traffic_curve(
        pattern=traffic_cfg["pattern"],
        peak_multiplier=traffic_cfg["peak_multiplier"],
        duration_minutes=traffic_cfg["duration_minutes"]
    )

    service_metrics = {}

    for service_name, service_cfg in base_services["services"].items():
        # Apply service overrides
        overrides = scenario.get("service_overrides", {}).get(service_name, {})

        base_latency = overrides.get(
            "base_latency_ms",
            service_cfg["base_latency_ms"]
        )

        queue_capacity = service_cfg["queue_capacity"]

        # Queue simulation
        queue_history = simulate_queue(
            traffic_curve=traffic_curve,
            queue_capacity=queue_capacity
        )
        queue_summary = summarize_queue(queue_history)

        # Latency computation
        latency_series = compute_latency_series(
            base_latency_ms=base_latency,
            queue_history=queue_history
        )
        peak_latency = summarize_latency(latency_series)

        service_metrics[service_name] = {
            "queue": queue_summary["max"],
            "latency_ms": peak_latency
        }

    return {
        "service_metrics": service_metrics
    }


def run_model_inference(simulation_metrics):
    """
    Stub ML inference.
    """
    return {
        service: {
            "stress_score": 0.0,
            "bottleneck_risk": 0.0
        }
        for service in simulation_metrics["service_metrics"].keys()
    }


def run_decision_engine(simulation_metrics, model_outputs, scaling_policy):
    """
    Stub decision engine.
    """
    return {
        "recommendations": [],
        "notes": "Decision engine not implemented yet."
    }


def create_run_dir():
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def write_json(run_dir, filename, data):
    with open(run_dir / filename, "w") as f:
        json.dump(data, f, indent=2)


def main():
    print("=== Capacity Planner Pipeline (Day 1 Stub) ===")

    base_services = load_base_services()
    scenario = load_scenario_config()

    print("Validating scenario...")
    validate_scenario(scenario)

    print("Running simulation...")
    simulation_metrics = run_simulation(base_services, scenario)

    print("Running model inference...")
    model_outputs = run_model_inference(simulation_metrics)

    print("Running decision engine...")
    recommendations = run_decision_engine(
        simulation_metrics,
        model_outputs,
        scenario["scaling_policy"]
    )

    run_dir = create_run_dir()
    print(f"Writing run artifacts to {run_dir}")

    write_json(run_dir, "config.json", scenario)
    write_json(run_dir, "metrics.json", simulation_metrics)
    write_json(run_dir, "stress_scores.json", model_outputs)
    write_json(run_dir, "recommendations.json", recommendations)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
