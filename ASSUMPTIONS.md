# Assumptions

This project is built under a set of explicit assumptions to ensure
determinism, auditability, and reproducibility.

These assumptions are deliberate design choices, not oversights.

---

## Synthetic Traffic Scenarios

All traffic patterns are synthetic and scenario-based.
They are designed to explore system stress behavior rather than
to replicate real production traffic distributions.

Traffic inputs are:
- bounded
- schema-validated
- deterministic per run

---

## Simplified Infrastructure Model

The infrastructure is abstracted using:
- queue length
- service latency
- dependency influence weights

The following are intentionally excluded:
- CPU and memory utilization
- network jitter
- retries and circuit breakers
- caching behavior

This abstraction allows clearer causal reasoning
about stress propagation across services.

---

## Static Service Topology

The service dependency graph is assumed to be:
- known
- static during a scenario run
- explicitly defined in configuration

Dynamic service discovery or topology changes
are outside the scope of this system.

---

## Bounded Rationality

The decision engine operates with bounded rationality:
- it uses fixed policies
- it relies on partial system signals
- it does not attempt global optimization

Recommendations are generated to assist human operators,
not to guarantee optimal outcomes.

---

## Deterministic Execution

Given the same configuration and random seed:
- simulation outputs are identical
- ML inference results are reproducible
- decision outputs do not change

This assumption is critical for auditability and post-incident analysis.
