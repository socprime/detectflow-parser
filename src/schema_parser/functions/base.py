from abc import ABC, abstractmethod
from typing import Any


class BaseFunction(ABC):
    """Base class for all data processing functions"""

    @abstractmethod
    def execute(self, data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """
        Executes the function on input data

        Args:
            data: Input data dictionary
            **kwargs: Function arguments

        Returns:
            Updated data dictionary
        """
        pass
