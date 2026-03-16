"""
Sigma rule validator.

Validates sigma rules BEFORE creating full Sigma objects to reject
unsupported rules early in the processing pipeline.
"""

import re

import yaml

from schema_parser.sigma_validation.exceptions import SigmaNotSupported
from schema_parser.sigma_validation.result import ValidationResult
from schema_parser.sigma_validation.supported import (
    SUPPORTED_MODIFIERS,
    UNSUPPORTED_CONDITION_FEATURES,
    UNSUPPORTED_MODIFIERS,
    UNSUPPORTED_RULE_TYPES,
    VALID_CONDITION_CHARS_PATTERN,
)


class SigmaValidator:
    """
    Validates sigma rules for supported features.

    This validator checks the structure and content of sigma rules without
    creating full Sigma/Signature objects, allowing early rejection of
    unsupported rules.
    """

    def validate(self, sigma_text: str) -> ValidationResult:
        """
        Validate a sigma rule text.

        Args:
            sigma_text: The raw YAML text of the sigma rule.

        Returns:
            ValidationResult with is_supported=True if valid,
            or is_supported=False with reason and unsupported_labels.
        """
        try:
            sigma_dict = self._parse_yaml(sigma_text)
        except SigmaNotSupported as e:
            return ValidationResult(
                is_supported=False,
                unsupported_reason=e.reason,
                unsupported_labels=e.unsupported_labels,
            )

        # Check for unsupported rule type (correlation rules)
        try:
            self._validate_rule_type(sigma_dict)
        except SigmaNotSupported as e:
            return ValidationResult(
                is_supported=False,
                unsupported_reason=e.reason,
                unsupported_labels=e.unsupported_labels,
            )

        # Validate detection section exists
        try:
            detection = self._validate_detection_section(sigma_dict)
        except SigmaNotSupported as e:
            return ValidationResult(
                is_supported=False,
                unsupported_reason=e.reason,
                unsupported_labels=e.unsupported_labels,
            )

        # Validate condition expression
        try:
            self._validate_condition(detection)
        except SigmaNotSupported as e:
            return ValidationResult(
                is_supported=False,
                unsupported_reason=e.reason,
                unsupported_labels=e.unsupported_labels,
            )

        # Validate modifiers in detection
        try:
            self._validate_modifiers(detection)
        except SigmaNotSupported as e:
            return ValidationResult(
                is_supported=False,
                unsupported_reason=e.reason,
                unsupported_labels=e.unsupported_labels,
            )

        return ValidationResult(is_supported=True)

    def validate_or_raise(self, sigma_text: str) -> None:
        """
        Validate a sigma rule and raise SigmaNotSupported if invalid.

        Args:
            sigma_text: The raw YAML text of the sigma rule.

        Raises:
            SigmaNotSupported: If the rule uses unsupported features.
        """
        result = self.validate(sigma_text)
        if not result.is_supported:
            raise SigmaNotSupported(
                reason=result.unsupported_reason or "Unknown validation error",
                unsupported_labels=result.unsupported_labels,
            )

    def _parse_yaml(self, sigma_text: str) -> dict:
        """Parse YAML text into a dictionary."""
        try:
            result = yaml.safe_load(sigma_text)
            if not isinstance(result, dict):
                raise SigmaNotSupported(
                    reason="Sigma rule must be a valid YAML dictionary",
                    unsupported_labels=["invalid_yaml_structure"],
                )
            return result
        except yaml.YAMLError as e:
            raise SigmaNotSupported(
                reason=f"Error parsing sigma YAML: {e}",
                unsupported_labels=["yaml_parse_error"],
            ) from e

    def _validate_rule_type(self, sigma_dict: dict) -> None:
        """Check if the rule is a correlation rule or other unsupported type."""
        rule_type = sigma_dict.get("type", "").lower()
        if rule_type in UNSUPPORTED_RULE_TYPES:
            raise SigmaNotSupported(
                reason=f"Unsupported rule type: {rule_type}",
                unsupported_labels=[f"rule_type:{rule_type}"],
            )

        # If it has 'correlation' key or looks like a correlation rule
        if "correlation" in sigma_dict:
            raise SigmaNotSupported(
                reason="Correlation rules are not supported",
                unsupported_labels=["correlation_rule"],
            )

        # Check if this is a correlation rule by looking for correlation-specific structure
        if sigma_dict.get("type") == "correlation" or (
            "group-by" in sigma_dict and "timespan" in sigma_dict
        ):
            raise SigmaNotSupported(
                reason="Correlation rules are not supported",
                unsupported_labels=["correlation_rule"],
            )

    def _validate_detection_section(self, sigma_dict: dict) -> dict:
        """Validate that detection section exists and is valid."""
        detection = sigma_dict.get("detection")
        if not detection:
            raise SigmaNotSupported(
                reason="Detection section not found in sigma rule",
                unsupported_labels=["missing_detection"],
            )
        if not isinstance(detection, dict):
            raise SigmaNotSupported(
                reason="Detection section must be a dictionary",
                unsupported_labels=["invalid_detection_type"],
            )
        if "condition" not in detection:
            raise SigmaNotSupported(
                reason="Condition not found in detection section",
                unsupported_labels=["missing_condition"],
            )
        return detection

    def _validate_condition(self, detection: dict) -> None:
        """Validate the condition expression."""
        condition = detection.get("condition", "")
        if not isinstance(condition, str):
            raise SigmaNotSupported(
                reason="Condition must be a string",
                unsupported_labels=["invalid_condition_type"],
            )

        # Check for unsupported condition features (aggregations, comparisons, etc.)
        condition_lower = condition.lower()
        for feature in UNSUPPORTED_CONDITION_FEATURES:
            if feature in condition_lower:
                raise SigmaNotSupported(
                    reason=f"Unsupported condition feature: {feature}",
                    unsupported_labels=[f"condition_feature:{feature}"],
                )

        # Normalize "all of" and "1 of" patterns
        normalized_condition = re.sub(r"all of ", "all_of_", condition, flags=re.IGNORECASE)
        normalized_condition = re.sub(r"1 of ", "1_of_", normalized_condition, flags=re.IGNORECASE)

        # Check for invalid characters in condition
        if not re.match(VALID_CONDITION_CHARS_PATTERN, normalized_condition):
            # Find the invalid characters
            invalid_chars = set(
                c for c in normalized_condition if not re.match(r"[a-zA-Z0-9_ \(\)\?\*]", c)
            )
            raise SigmaNotSupported(
                reason=f"Invalid characters in condition: {invalid_chars}",
                unsupported_labels=["invalid_condition_chars"],
            )

        # Validate "all of" and "1 of" patterns
        if "all_of_" in normalized_condition or "1_of_" in normalized_condition:
            # Must have wildcard pattern or "them"
            if (
                "*" not in normalized_condition
                and "?" not in normalized_condition
                and not normalized_condition.endswith("of_them")
                and "of_them " not in normalized_condition
                and "of_them)" not in normalized_condition
            ):
                raise SigmaNotSupported(
                    reason="'all of' or '1 of' conditions must use a pattern (wildcard) or 'them'",
                    unsupported_labels=["invalid_of_pattern"],
                )

        # Validate that referenced conditions exist in detection
        self._validate_condition_references(normalized_condition, detection)

    def _validate_condition_references(self, normalized_condition: str, detection: dict) -> None:
        """Validate that all condition references exist in detection."""
        # Extract all tokens from condition
        tokens = re.findall(r"[a-zA-Z0-9_\*\?]+", normalized_condition)

        reserved_words = {"and", "or", "not", "all_of_them", "1_of_them"}
        detection_keys = set(detection.keys()) - {"condition"}

        for token in tokens:
            token_lower = token.lower()
            # Skip reserved words
            if token_lower in reserved_words:
                continue
            # Skip "all_of_X" and "1_of_X" - they reference patterns
            if token_lower.startswith("all_of_") or token_lower.startswith("1_of_"):
                continue

            # For regular condition names, check if they exist
            if token not in detection_keys:
                # Check if it might be a pattern reference (contains wildcards)
                if "*" in token or "?" in token:
                    continue
                # Condition reference not found
                raise SigmaNotSupported(
                    reason=f"Condition '{token}' not found in detection",
                    unsupported_labels=[f"missing_condition_ref:{token}"],
                )

    def _validate_modifiers(self, detection: dict) -> None:
        """Validate modifiers used in field names."""
        unsupported_found: list[str] = []

        for key, value in detection.items():
            if key == "condition":
                continue

            # Check field definitions in each detection item
            if isinstance(value, dict):
                self._check_dict_modifiers(value, unsupported_found)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._check_dict_modifiers(item, unsupported_found)

        if unsupported_found:
            unique_modifiers = sorted(set(unsupported_found))
            raise SigmaNotSupported(
                reason=f"Unsupported modifiers: {', '.join(unique_modifiers)}",
                unsupported_labels=[f"modifier:{m}" for m in unique_modifiers],
            )

    def _check_dict_modifiers(self, d: dict, unsupported_found: list[str]) -> None:
        """Check modifiers in a detection dictionary."""
        for field_key in d.keys():
            # Field keys can have modifiers separated by |
            # e.g., "CommandLine|contains|all"
            parts = str(field_key).split("|")
            if len(parts) > 1:
                # First part is the field name, rest are modifiers
                modifiers = parts[1:]
                for modifier in modifiers:
                    modifier_lower = modifier.lower()
                    if modifier_lower in UNSUPPORTED_MODIFIERS:
                        unsupported_found.append(modifier_lower)
                    elif modifier_lower not in SUPPORTED_MODIFIERS:
                        # Unknown modifier - treat as unsupported
                        unsupported_found.append(modifier_lower)
