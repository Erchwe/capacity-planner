# AI-Assisted Service Capacity & Scaling Planner

This project is a **decision-support system** designed to help infrastructure and platform teams
analyze service stress, saturation risk, and scaling needs under different traffic scenarios.

The system intentionally **does not perform auto-scaling**.
Instead, it combines:
- a deterministic simulation engine
- a graph-based ML advisory model
- a rule-constrained decision engine

to produce **auditable, reproducible scaling recommendations**.

---

## What Problem Does This Solve?

Modern service architectures often fail under stress not because of raw lack of capacity,
but due to **coordination breakdown**, such as:
- queue buildup
- latency amplification
- cascading dependency slowdowns

This system helps engineers:
- understand where stress accumulates
- identify bottleneck risks
- reason about scaling decisions *before* incidents happen

---

## Why Is ML Used Only as an Advisory Layer?

Machine learning in this system:
- does **not** control infrastructure
- does **not** trigger scaling actions
- cannot override simulation outputs or policy constraints

ML is used to:
- estimate stress likelihood
- highlight potential bottlenecks
- assist human decision-making

This preserves:
- auditability
- operational safety
- reproducibility

---

## System Architecture (Execution Flow)

The system follows a layered, deterministic execution pipeline:

Scenario Input  
↓  
Validation Layer  
↓  
Traffic Generator  
↓  
Queue Simulation  
↓  
Latency Propagation  
↓  
Graph-Aware Advisory Layer  
↓  
Policy-Based Decision Engine  
↓  
Structured Run Artifacts (JSON)

Each layer has a clearly bounded responsibility:

- Simulation produces ground-truth stress metrics
- Advisory layer estimates risk likelihood
- Decision engine applies policy constraints
- Outputs remain structured and reproducible

---

## Simulation Core (Deterministic Ground Truth)

The simulation engine serves as the system’s ground truth layer.

It models service behavior using:
- scenario-based traffic patterns (steady, spike, ramp)
- queue buildup under load
- latency amplification caused by queue pressure

All simulations are:
- deterministic
- seed-free
- reproducible given the same configuration

The simulation intentionally avoids real-time metrics or stochastic behavior
to preserve causal clarity and auditability.

---

## ML Advisory Layer

The system includes a deterministic graph-aware advisory model inspired
by message passing neural networks (GNN-style propagation).

This layer:

- Computes local stress signals based on queue utilization and latency ratio
- Propagates stress across service dependencies
- Outputs calibrated risk scores in the range [0, 1]
- Remains deterministic and fully auditable

Important:
The advisory layer does NOT modify simulation outputs.
It provides recommendation signals only.

---

## Core Components

### 1. Traffic Simulation
Generates synthetic traffic curves based on validated scenario inputs.
Supports steady, spike, and ramp patterns.

### 2. Queue Engine
Models bounded queue growth under sustained or burst load.
Outputs peak queue saturation per service.

### 3. Latency Propagation
Propagates latency influence across service dependencies
using weighted graph relationships.

### 4. Advisory Risk Scoring
Computes calibrated stress likelihood scores in the range [0, 1].
Risk is derived from:
- queue saturation ratio
- latency amplification ratio
- dependency influence weights

### 5. Decision Engine
Applies deterministic, rule-based scaling policies.
Supports:
- scale_up_aggressive
- scale_up_cautious
- no_action

Includes topology-aware reinforcement for upstream services.

---

## How to Run (Day 1 Stub)

Install minimal dependencies:

```
pip install pyyaml jsonschema
```

Run the pipeline:

```
python scripts/run_pipeline.py
```

This will execute a stubbed end-to-end pipeline and generate
a reproducible run artifact under the `runs/` directory.

---

## Design Principles

- Deterministic core execution
- Bounded and explainable advisory logic
- Strict separation between simulation and decision layers
- No hidden optimization loops
- Reproducible run artifacts for post-analysis

The system prioritizes interpretability over automation.

---

## Roadmap

Current capabilities:

- [x] Deterministic traffic simulation
- [x] Queue saturation modeling
- [x] Dependency-aware latency propagation
- [x] Graph-inspired advisory risk scoring
- [x] Topology-aware decision engine

Planned improvements:

- [ ] CLI-based dynamic scenario input
- [ ] REST API interface
- [ ] Web dashboard visualization
- [ ] Containerized deployment

## What This Project Is NOT

- Not a real-time system
- Not an auto-scaling controller
- Not a production-ready infrastructure tool
- Not a machine-learning-first demo

This project prioritizes **clarity, determinism, and explainability**
over automation or performance optimizations.
