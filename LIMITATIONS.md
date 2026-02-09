# Limitations

This system is intentionally limited in scope.
The following limitations are acknowledged and accepted
as part of the design.

---

## No Real-Time Operation

All analyses are performed offline using predefined scenarios.
The system does not ingest live metrics, logs, or telemetry streams.

It is not intended for real-time incident response or monitoring.

---

## No Automatic Scaling

The system does not execute scaling actions.
All scaling outputs are advisory recommendations only.

There is no direct integration with:
- cloud provider APIs
- orchestration platforms
- auto-scaling controllers

---

## Synthetic Data Only

The machine learning model is trained exclusively
on simulation-generated data.

No production telemetry is used,
and model outputs should not be interpreted
as predictive guarantees for real systems.

---

## Simplified Dependency Modeling

Service dependencies are modeled as weighted directed edges.

The system does not capture:
- retry storms
- cascading failures due to misconfiguration
- stateful degradation patterns

These behaviors would require a significantly more complex model
and are intentionally excluded to preserve explainability.

---

## Not a Production System

This project is a design and engineering demonstration.
It is not hardened for production use.

Missing production features include:
- authentication and authorization
- failure recovery
- observability and alerting
- operational runbooks
