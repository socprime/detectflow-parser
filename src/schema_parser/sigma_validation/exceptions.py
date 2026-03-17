"""Exceptions for sigma validation module."""


class SigmaNotSupported(Exception):  # noqa: N818
    """Raised when a sigma rule uses unsupported features."""

    def __init__(self, reason: str, unsupported_labels: list[str] | None = None):
        self.reason = reason
        self.unsupported_labels = unsupported_labels or []
        super().__init__(reason)
