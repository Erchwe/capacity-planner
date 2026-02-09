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

## System Architecture (High-Level)

Scenario Config  
→ Validation Layer  
→ Simulation Engine (ground truth)  
→ ML Advisory Model (GNN)  
→ Decision Engine  
→ Structured Outputs (JSON)  
→ Read-only Dashboard  

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

## What This Project Is NOT

- Not a real-time system
- Not an auto-scaling controller
- Not a production-ready infrastructure tool
- Not a machine-learning-first demo

This project prioritizes **clarity, determinism, and explainability**
over automation or performance optimizations.
