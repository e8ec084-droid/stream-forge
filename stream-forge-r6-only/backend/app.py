from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Stream Forge R6 Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Stream Forge R6 FastAPI stub is running"}

@app.get("/api/week1")
def get_week1():
    return {
        "nodes": [
            {"id": "producer", "label": "Kafka Producer", "status": "healthy", "type": "input"},
            {"id": "consume", "label": "Consume", "status": "healthy", "type": "stage"},
            {"id": "filter", "label": "Filter Temp > 0", "status": "healthy", "type": "stage"},
            {"id": "map", "label": "Map Transform", "status": "healthy", "type": "stage"},
            {"id": "window", "label": "5-min Window", "status": "healthy", "type": "stage"},
            {"id": "sink", "label": "Output Topic", "status": "healthy", "type": "output"}
        ],
        "edges": [
            ["producer", "consume"],
            ["consume", "filter"],
            ["filter", "map"],
            ["map", "window"],
            ["window", "sink"]
        ]
    }

@app.get("/api/week2")
def get_week2():
    return {
        "nodes": [
            {"id": "producer", "label": "Kafka Producer", "status": "healthy", "type": "input"},
            {"id": "consume", "label": "Consume", "status": "healthy", "type": "stage"},
            {"id": "filter", "label": "Filter Temp > 0", "status": "healthy", "type": "stage"},
            {"id": "map", "label": "Map Transform", "status": "warning", "type": "stage"},
            {"id": "window", "label": "5-min Window", "status": "healthy", "type": "stage"},
            {"id": "sink", "label": "Output Topic", "status": "healthy", "type": "output"}
        ],
        "edges": [
            ["producer", "consume"],
            ["consume", "filter"],
            ["filter", "map"],
            ["map", "window"],
            ["window", "sink"]
        ],
        "workers": [
            {"id": "worker-1", "health": "healthy", "lag": 9},
            {"id": "worker-2", "health": "healthy", "lag": 15},
            {"id": "worker-3", "health": "warning", "lag": 41}
        ],
        "metrics": {
            "throughput": 98234,
            "target": 100000,
            "active_partitions": 4
        }
    }

@app.get("/api/mid-review")
def get_mid_review():
    return {
        "throughput": {
            "current": 100842,
            "target": 100000,
            "status": "pass"
        },
        "partitions": [
            {"partition": 0, "eps": 25120, "health": "healthy"},
            {"partition": 1, "eps": 24880, "health": "healthy"},
            {"partition": 2, "eps": 25410, "health": "healthy"},
            {"partition": 3, "eps": 25432, "health": "healthy"}
        ],
        "windowing": {
            "rolling_average_correct": True,
            "late_arrivals_handled": True,
            "status": "verified",
            "note": "Validated against audit sample dataset"
        },
        "workers": [
            {"id": "worker-1", "health": "healthy"},
            {"id": "worker-2", "health": "healthy"},
            {"id": "worker-3", "health": "healthy"}
        ]
    }
