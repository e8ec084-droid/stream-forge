from dataclasses import dataclass

@dataclass
class TruckState:
    """
    Represents the latest aggregated state of a truck.
    """

    truck_id: str

    avg_temperature: float

    event_count: int

    window_start: int

    window_end: int

    status: str = "healthy"