from fastapi import FastAPI
from pydantic import BaseModel

from scripts.run_pipeline import execute_pipeline, load_base_services

app = FastAPI(title="Capacity Planner API")


class ScenarioInput(BaseModel):
    pattern: str = "spike"
    peak: float = 3.0
    duration: int = 20
    risk_tolerance: str = "conservative"


@app.post("/run")
def run_capacity_planner(input: ScenarioInput):
    base_services = load_base_services()

    scenario = {
        "traffic": {
            "pattern": input.pattern,
            "peak_multiplier": input.peak,
            "duration_minutes": input.duration
        },
        "service_overrides": {},
        "scaling_policy": {
            "aggressiveness": "medium",
            "cooldown_minutes": 10,
            "risk_tolerance": input.risk_tolerance
        }
    }

    result = execute_pipeline(base_services, scenario)
    return result
