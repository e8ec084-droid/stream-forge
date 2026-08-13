"""Exposes R5's metrics to Prometheus and to R6's React Flow dashboard (Week 4, Tuesday).

R6's ``dashboard_service.py`` already has a placeholder for a real metrics
feed ("Connect FastAPI metrics endpoint (stub)"). This module is that real
endpoint's source of truth — it's a separate service, not a change to R6's
code, so R6 can point at it whenever they wire the stub up for real.
"""

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from stream_forge_r5.metrics import registry

app = FastAPI(title="Stream Forge R5 Observability API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def scrape_metrics() -> PlainTextResponse:
    """Standard Prometheus scrape target — same shape R1/R6 already expect from FastAPI."""
    return PlainTextResponse(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
