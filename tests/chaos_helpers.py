from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def inject_failure(target, method, error=None):
    """Temporarily replace a method with one that raises an injected failure."""
    error = error or RuntimeError("injected chaos failure")

    def fail(*args, **kwargs):
        raise error

    with patch.object(target, method, side_effect=fail):
        yield
