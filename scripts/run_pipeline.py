import sys
import argparse
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
from simulator.propagate import propagate_dependency_latency
from ml.advisory import compute_service_risk_scores

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE_DIR / "configs"
RUNS_DIR = BASE_DIR / "runs"


def load_base_services():
    with open(CONFIG_DIR / "base_services.yaml", "r") as f:
        return yaml.safe_load(f)


def load_scenario_from_args():
    parser = argparse.ArgumentParser(
        description="Run capacity planner with dynamic scenario input."
    )

    parser.add_argument("--pattern", type=str, default="spike",
                        choices=["steady", "spike", "ramp"],
                        help="Traffic pattern type")

    parser.add_argument("--peak", type=float, default=3.0,
                        help="Peak multiplier for traffic")

    parser.add_argument("--duration", type=int, default=20,
                        help="Duration in minutes")

    parser.add_argument("--risk_tolerance", type=str, default="conservative",
                        choices=["conservative", "moderate", "aggressive"],
                        help="Scaling risk tolerance")

    args = parser.parse_args()

    return {
        "traffic": {
            "pattern": args.pattern,
            "peak_multiplier": args.peak,
            "duration_minutes": args.duration
        },
        "service_overrides": {},
        "scaling_policy": {
            "aggressiveness": "medium",
            "cooldown_minutes": 10,
            "risk_tolerance": args.risk_tolerance
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
    
        # Collect local peak latencies
    local_latencies = {
        svc: metrics["latency_ms"]
        for svc, metrics in service_metrics.items()
    }

    # Dependency graph from base config
    dependency_graph = {
        svc: cfg.get("dependencies", {})
        for svc, cfg in base_services["services"].items()
    }

    # Propagate dependency effects
    effective_latencies = propagate_dependency_latency(
        local_latencies=local_latencies,
        service_dependencies=dependency_graph
    )

    # Update metrics with propagated latency
    for svc in service_metrics:
        service_metrics[svc]["latency_ms"] = effective_latencies[svc]

    return {
        "service_metrics": service_metrics
    }


def run_model_inference(simulation_metrics, base_services):
    """
    Deterministic graph-aware advisory scoring.
    """

    service_metrics = simulation_metrics["service_metrics"]

    risk_scores = compute_service_risk_scores(
        service_metrics=service_metrics,
        base_services=base_services
    )

    model_outputs = {
        service: {
            "risk_score": risk_scores[service],
            "bottleneck_risk": risk_scores[service]
        }
        for service in risk_scores
    }

    return model_outputs



def run_decision_engine(simulation_metrics, model_outputs, scaling_policy, base_services):
    """
    Deterministic rule-based scaling recommendations
    with topology-aware reinforcement.
    """

    HIGH_RISK = 0.80
    MEDIUM_RISK = 0.65

    recommendations = {}
    service_metrics = simulation_metrics["service_metrics"]

    dependency_graph = {
        svc: cfg.get("dependencies", {})
        for svc, cfg in base_services["services"].items()
    }

    # First pass: primary decisions
    for service, model_data in model_outputs.items():
        risk = model_data["risk_score"]
        queue = service_metrics[service]["queue"]

        if risk >= HIGH_RISK:
            recommendations[service] = {
                "action": "scale_up_aggressive",
                "risk_score": round(risk, 3),
                "queue_level": queue,
                "reason": f"High risk score ({risk:.2f}) indicates severe stress."
            }
        elif risk >= MEDIUM_RISK:
            recommendations[service] = {
                "action": "scale_up_cautious",
                "risk_score": round(risk, 3),
                "queue_level": queue,
                "reason": f"Moderate risk score ({risk:.2f}) suggests rising load."
            }

    # Second pass: upstream reinforcement
    for service, rec in list(recommendations.items()):
        if rec["action"] == "scale_up_aggressive":
            dependencies = dependency_graph.get(service, {})

            for upstream_service in dependencies.keys():
                if upstream_service not in recommendations:
                    upstream_risk = model_outputs[upstream_service]["risk_score"]
                    recommendations[upstream_service] = {
                        "action": "scale_up_cautious",
                        "risk_score": round(upstream_risk, 3),
                        "queue_level": service_metrics[upstream_service]["queue"],
                        "reason": f"Upstream dependency of aggressively scaled service '{service}'."
                    }

    return {
        "recommendations": [
            {"service": svc, **rec}
            for svc, rec in recommendations.items()
        ],
        "policy_used": scaling_policy
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
    print("=== Capacity Planner Pipeline ===")

    base_services = load_base_services()
    scenario = load_scenario_from_args()

    print("Validating scenario...")
    validate_scenario(scenario)

    print("Running simulation...")
    simulation_metrics = run_simulation(base_services, scenario)

    print("Running model inference...")
    model_outputs = run_model_inference(
        simulation_metrics,
        base_services
    )

    print("Running decision engine...")
    recommendations = run_decision_engine(
        simulation_metrics,
        model_outputs,
        scenario["scaling_policy"],
        base_services
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
