from typing import Literal

from pydantic import BaseModel


HealthStatus = Literal["healthy", "warning", "critical"]
NodeKind = Literal["input", "stage", "output"]


class TopologyNode(BaseModel):
    id: str
    label: str
    status: HealthStatus
    type: NodeKind


class TopologyEdge(BaseModel):
    source: str
    target: str


class WorkerMetric(BaseModel):
    id: str
    health: HealthStatus
    lag: int | None = None


class ThroughputMetrics(BaseModel):
    throughput: int
    target: int
    active_partitions: int | None = None


class Week1Response(BaseModel):
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]


class Week2Response(BaseModel):
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]
    workers: list[WorkerMetric]
    metrics: ThroughputMetrics


class PartitionMetric(BaseModel):
    partition: int
    eps: int
    health: HealthStatus


class ThroughputAudit(BaseModel):
    current: int
    target: int
    status: Literal["pass", "fail", "warning"]


class WindowingAudit(BaseModel):
    rolling_average_correct: bool
    late_arrivals_handled: bool
    status: Literal["verified", "warning", "failed"]
    note: str


class MidReviewResponse(BaseModel):
    throughput: ThroughputAudit
    partitions: list[PartitionMetric]
    windowing: WindowingAudit
    workers: list[WorkerMetric]
