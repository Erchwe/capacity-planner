# Simulation Engine

The simulation engine provides a deterministic approximation of service behavior
under varying traffic conditions.

## Modeled Concepts

The simulator models:
- traffic load over time
- queue buildup due to excess demand
- latency increase caused by queue pressure

Each simulation step represents one minute.

## What Is Intentionally Not Modeled

The simulator does not model:
- CPU or memory utilization
- retries or circuit breakers
- network-level effects
- autoscaling behavior

These exclusions are deliberate to preserve simplicity,
interpretability, and reproducibility.

## Role in the System

The simulation engine acts as the ground truth layer.
Machine learning models consume simulation outputs
but never override or replace them.
