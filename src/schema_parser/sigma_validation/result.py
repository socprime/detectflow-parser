"""Validation result for sigma rules."""

from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of sigma rule validation."""

    is_supported: bool
    unsupported_reason: str | None = None
    unsupported_labels: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.unsupported_labels is None:
            self.unsupported_labels = []
