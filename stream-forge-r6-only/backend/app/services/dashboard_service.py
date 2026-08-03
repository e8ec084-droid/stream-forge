from app.schemas.dashboard import (
    MidReviewResponse,
    PartitionMetric,
    ThroughputAudit,
    ThroughputMetrics,
    TopologyEdge,
    TopologyNode,
    Week1Response,
    Week2Response,
    WindowingAudit,
    WorkerMetric,
)


class DashboardService:
    def get_week1_dashboard(self) -> Week1Response:
        return Week1Response(
            nodes=[
                TopologyNode(id="producer", label="Kafka Producer", status="healthy", type="input"),
                TopologyNode(id="consume", label="Consume", status="healthy", type="stage"),
                TopologyNode(id="filter", label="Filter Temp > 0", status="healthy", type="stage"),
                TopologyNode(id="map", label="Map Transform", status="healthy", type="stage"),
                TopologyNode(id="window", label="5-min Window", status="healthy", type="stage"),
                TopologyNode(id="sink", label="Output Topic", status="healthy", type="output"),
            ],
            edges=[
                TopologyEdge(source="producer", target="consume"),
                TopologyEdge(source="consume", target="filter"),
                TopologyEdge(source="filter", target="map"),
                TopologyEdge(source="map", target="window"),
                TopologyEdge(source="window", target="sink"),
            ],
        )

    def get_week2_dashboard(self) -> Week2Response:
        return Week2Response(
            nodes=[
                TopologyNode(id="producer", label="Kafka Producer", status="healthy", type="input"),
                TopologyNode(id="consume", label="Consume", status="healthy", type="stage"),
                TopologyNode(id="filter", label="Filter Temp > 0", status="healthy", type="stage"),
                TopologyNode(id="map", label="Map Transform", status="warning", type="stage"),
                TopologyNode(id="window", label="5-min Window", status="healthy", type="stage"),
                TopologyNode(id="sink", label="Output Topic", status="healthy", type="output"),
            ],
            edges=[
                TopologyEdge(source="producer", target="consume"),
                TopologyEdge(source="consume", target="filter"),
                TopologyEdge(source="filter", target="map"),
                TopologyEdge(source="map", target="window"),
                TopologyEdge(source="window", target="sink"),
            ],
            workers=[
                WorkerMetric(id="worker-1", health="healthy", lag=9),
                WorkerMetric(id="worker-2", health="healthy", lag=15),
                WorkerMetric(id="worker-3", health="warning", lag=41),
            ],
            metrics=ThroughputMetrics(
                throughput=98234,
                target=100000,
                active_partitions=4,
            ),
        )

    def get_mid_review_dashboard(self) -> MidReviewResponse:
        return MidReviewResponse(
            throughput=ThroughputAudit(current=100842, target=100000, status="pass"),
            partitions=[
                PartitionMetric(partition=0, eps=25120, health="healthy"),
                PartitionMetric(partition=1, eps=24880, health="healthy"),
                PartitionMetric(partition=2, eps=25410, health="healthy"),
                PartitionMetric(partition=3, eps=25432, health="healthy"),
            ],
            windowing=WindowingAudit(
                rolling_average_correct=True,
                late_arrivals_handled=True,
                status="verified",
                note="Validated against audit sample dataset",
            ),
            workers=[
                WorkerMetric(id="worker-1", health="healthy"),
                WorkerMetric(id="worker-2", health="healthy"),
                WorkerMetric(id="worker-3", health="healthy"),
            ],
        )
