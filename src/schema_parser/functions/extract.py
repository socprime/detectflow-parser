from typing import Any

from schema_parser.core.utils import delete_value, get_value, is_empty_value

from .base import BaseFunction


class ExtractFunction(BaseFunction):
    """Function for extracting a nested dictionary and merging it with the parent"""

    def execute(self, data: dict[str, Any], field: str) -> dict[str, Any]:
        """
        Extracts a nested dictionary from the specified field and merges it with the parent.

        Args:
            data: Input data dictionary
            field: Name of the field containing the nested dictionary to extract.
                  Supports dot-separated paths like "user.profile" or "winlog.event_data".

        Returns:
            Updated data dictionary with nested fields merged at the top level

        Example:
            Input: {'user': {'user_name': 'test', 'user_id': '1'}, 'some_field': 'some_value'}
            After extract(field="user"):
            Output: {'user_name': 'test', 'user_id': '1', 'some_field': 'some_value'}
        """
        field_value = get_value(data, field)

        if field_value is None:
            # Silently ignore if field is not found
            return data

        # Treat null, empty string, and empty array as empty (ignore them)
        # But empty dict is valid and should be extracted
        if is_empty_value(field_value) and not isinstance(field_value, dict):
            return data

        nested_dict = delete_value(data, field)

        if nested_dict is None:
            return data

        if not isinstance(nested_dict, dict):
            raise ValueError(f"Field {field} does not contain a dictionary")

        # Merge the nested dictionary into the parent (even if it's empty)
        data.update(nested_dict)
        return data
