class RegexFunctionError(Exception):
    """Base exception for regex function errors"""

    def __init__(self, message: str, field: str | None = None, pattern: str | None = None):
        self.field = field
        self.pattern = pattern
        super().__init__(message)


class RegexFieldTypeError(RegexFunctionError):
    """Error: field is not a string"""

    def __init__(self, field: str, field_type: type):
        message = f"Field '{field}' has type {field_type.__name__}, expected str"
        super().__init__(message, field=field)


class RegexPatternMatchError(RegexFunctionError):
    """Error: failed to find pattern match"""

    def __init__(self, field: str, pattern: str, field_value: str):
        if len(field_value) > 100:
            message = (
                f"Failed to find pattern match '{pattern}' "
                f"in field '{field}' with value '{field_value[:100]}...'"
            )
        else:
            message = (
                f"Failed to find pattern match '{pattern}' "
                f"in field '{field}' with value '{field_value}'"
            )
        super().__init__(message, field=field, pattern=pattern)


class RegexFunctionUnexpectedError(RegexFunctionError):
    """Unexpected error during regex function execution"""

    def __init__(self, field: str | None, pattern: str | None, original_error: Exception):
        message = f"Unexpected error during regex execution: {str(original_error)}"
        super().__init__(message, field=field, pattern=pattern)
        self.original_error = original_error


class ParseJsonFunctionError(Exception):
    """Error during JSON parsing"""

    def __init__(self, message: str, field: str | None = None, field_value: str | None = None):
        self.field = field
        self.field_value = field_value
        super().__init__(message)
