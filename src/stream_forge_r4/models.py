from dataclasses import dataclass


@dataclass
class TruckState:
    """
    Current state maintained for each truck.
    """

    truck_id: str
    last_temperature: float
    event_count: int
    last_timestamp: int
    status: str = "healthy"