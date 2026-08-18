class StateStoreError(Exception):
    """Base exception for the RocksDB state store."""


class StateNotFoundError(StateStoreError):
    """Raised when a requested truck state is not found."""
