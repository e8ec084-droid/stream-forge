from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any
from unittest.mock import patch


@contextmanager
def inject_failure(
    target: Any,
    method: str,
    error: BaseException | None = None,
) -> Iterator[None]:
    """Temporarily replace a method with one that raises an injected failure."""
    error = error or RuntimeError("injected chaos failure")

    def fail(*args: Any, **kwargs: Any) -> None:
        raise error

    with patch.object(target, method, side_effect=fail):
        yield
