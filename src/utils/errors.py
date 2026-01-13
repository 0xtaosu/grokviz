"""Custom exception classes for GrokViz."""


class GrokVizError(Exception):
    """Base exception for all GrokViz errors."""

    def __init__(self, message: str, error_code: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}

    def __str__(self):
        base = f"[{self.error_code}] {self.message}" if self.error_code else self.message
        if self.context:
            base += f" | Context: {self.context}"
        return base


class EmailFetchError(GrokVizError):
    """Raised when email retrieval fails."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, error_code="EMAIL_FETCH_ERROR", context=context)


class EmailParseError(GrokVizError):
    """Raised when email parsing fails."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, error_code="EMAIL_PARSE_ERROR", context=context)


class DataProcessingError(GrokVizError):
    """Raised when data extraction or processing fails."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, error_code="DATA_PROCESSING_ERROR", context=context)


class InfographicGenerationError(GrokVizError):
    """Raised when infographic generation fails."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, error_code="INFOGRAPHIC_GENERATION_ERROR", context=context)


class TelegramSendError(GrokVizError):
    """Raised when Telegram message sending fails."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, error_code="TELEGRAM_SEND_ERROR", context=context)


class ConfigurationError(GrokVizError):
    """Raised when configuration is invalid or missing."""

    def __init__(self, message: str, context: dict = None):
        super().__init__(message, error_code="CONFIGURATION_ERROR", context=context)
