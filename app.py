from fastapi import FastAPI
from pydantic import BaseModel

from scripts.run_pipeline import execute_pipeline, load_base_services

from logging_config import setup_logging
import time
import uuid

logger = setup_logging()

app = FastAPI(title="Capacity Planner API")

class ScenarioInput(BaseModel):
    pattern: str = "spike"
    peak: float = 3.0
    duration: int = 20
    risk_tolerance: str = "conservative"


@app.post("/run")
def run_capacity_planner(input: ScenarioInput):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        "Scenario execution started",
        extra={
            "extra_fields": {
                "request_id": request_id,
                "pattern": input.pattern,
                "peak": input.peak,
                "duration": input.duration,
                "risk_tolerance": input.risk_tolerance
            }
        }
    )

    try:
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

        recommendation_count = len(
            result.get("recommendations", {}).get("recommendations", [])
        )

        execution_time = round(time.time() - start_time, 4)

        logger.info(
            "Scenario execution completed",
            extra={
                "extra_fields": {
                    "request_id": request_id,
                    "execution_time_seconds": execution_time,
                    "recommendation_count": recommendation_count
                }
            }
        )

        return result

    except Exception as e:
        logger.exception(
            "Scenario execution failed",
            extra={
                "extra_fields": {
                    "request_id": request_id,
                    "error": str(e)
                }
            }
        )
        raise