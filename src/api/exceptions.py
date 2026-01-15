"""Custom exception handlers for FastAPI."""

import logging
import os

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from tenacity import RetryError

logger = logging.getLogger(__name__)


def setup_exception_handlers(app) -> None:
    """
    Setup custom exception handlers for the FastAPI app.

    This function registers exception handlers to provide better error messages
    for common issues like JSON parsing errors (e.g., trailing commas).
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Custom exception handler for validation errors.

        Improves error messages for common JSON errors, especially trailing commas
        that can occur when copy-pasting from Swagger UI.

        How it works:
        - Detects JSON decode errors (type: "json_invalid")
        - Checks for common error messages like "Expecting property name" which often
          indicates a trailing comma (e.g., `{"key": "value",}` is invalid JSON)
        - Provides a helpful message explaining the likely cause instead of the raw error
        """
        errors = exc.errors()

        # Check if it's a JSON decode error
        for error in errors:
            if error.get("type") == "json_invalid":
                error_msg = error.get("ctx", {}).get("error", "")

                # Check for common JSON errors
                # "Expecting property name" typically means a trailing comma or syntax error
                # Example: {"key": "value",} -> expects another property after the comma
                if "Expecting property name" in error_msg or "Invalid \\escape" in error_msg:
                    # Provide a helpful message explaining common causes
                    detail = (
                        "Invalid JSON format. "
                        "Common causes: trailing comma at the end of an array or object "
                        "(e.g., `[...],` or `{...},`), or improperly escaped characters. "
                        f"Original error: {error_msg}"
                    )

                    return JSONResponse(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={"detail": detail},
                    )

        # For other validation errors, return simplified format
        # Extract the first error message for clarity
        if errors:
            first_error = errors[0]
            error_type = first_error.get("type", "validation_error")
            error_loc = " -> ".join(str(loc) for loc in first_error.get("loc", []))
            error_msg = first_error.get("msg", "Validation error")

            # Create a user-friendly message
            if error_type == "missing":
                detail = f"Missing required field: '{error_loc}'. Please provide this field in your request."
            elif error_type == "value_error":
                detail = f"Invalid value for field '{error_loc}': {error_msg}"
            else:
                detail = f"Validation error in field '{error_loc}': {error_msg}"

            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": detail},
            )

        # Fallback to default format
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors},
        )


def format_error_message(exception: Exception, context: str = "") -> str:
    """
    Format exception into a user-friendly error message.

    Handles common exceptions and extracts meaningful messages:
    - ValueError: Uses the message directly (usually clear)
    - RetryError (Tenacity): Extracts the original exception
    - OpenAI API errors: Converts to user-friendly messages
    - Generic exceptions: Provides safe message

    Args:
        exception: The exception to format
        context: Additional context (e.g., "question generation", "LLM simulation")

    Returns:
        User-friendly error message
    """
    # Handle RetryError (from Tenacity) - extract the original exception
    if isinstance(exception, RetryError):
        # RetryError.last_attempt contains the last attempt's exception
        if hasattr(exception, "last_attempt") and exception.last_attempt.exception():
            original_exception = exception.last_attempt.exception()
            return format_error_message(original_exception, context)

    # Handle ValueError (usually clear messages from our code)
    if isinstance(exception, ValueError):
        error_msg = str(exception)

        # API key errors
        if "API_KEY" in error_msg or "api key" in error_msg.lower():
            if "OPENAI" in error_msg:
                return "OpenAI API key not configured. Please set OPENAI_API_KEY in your environment variables."
            elif "TAVILY" in error_msg:
                return "Tavily API key not configured. Please set TAVILY_API_KEY in your environment variables."
            return "API key not configured. Please check your environment variables."

        # Provider/model errors
        if "provider" in error_msg.lower() or "llm_spec" in error_msg.lower():
            if "not yet implemented" in error_msg.lower():
                return f"Provider not yet implemented. {error_msg}"
            elif "Unsupported provider" in error_msg:
                return f"Unsupported LLM provider. {error_msg}"
            elif "Invalid llm_spec format" in error_msg:
                return f"Invalid LLM specification format. {error_msg}"
            return error_msg

        # Format errors
        if "format" in error_msg.lower():
            return error_msg

        # Generic ValueError
        return error_msg

    # Handle OpenAI API errors (NotFoundError, etc.)
    error_type = type(exception).__name__
    error_msg = str(exception)

    # OpenAI model not found
    if "NotFoundError" in error_type or "not found" in error_msg.lower():
        # Try to extract model name from error message
        if "model" in error_msg.lower():
            return (
                f"LLM model not found. The model name you provided doesn't exist or is invalid. "
                f"Please check the model name (e.g., 'gpt-4', 'gpt-4o-mini'). "
                f"Error: {error_msg}"
            )
        return f"Resource not found. {error_msg}"

    # OpenAI authentication errors
    if (
        "AuthenticationError" in error_type
        or "authentication" in error_msg.lower()
        or "unauthorized" in error_msg.lower()
    ):
        return "Authentication failed. Please check your API key and ensure it's valid."

    # OpenAI rate limit errors
    if "RateLimitError" in error_type or "rate limit" in error_msg.lower():
        return "Rate limit exceeded. Please wait a moment and try again."

    # OpenAI timeout errors
    if "TimeoutError" in error_type or "timeout" in error_msg.lower():
        return "Request timed out. The API took too long to respond. Please try again."

    # Connection errors
    if "ConnectionError" in error_type or "connection" in error_msg.lower():
        return "Connection error. Unable to reach the API. Please check your internet connection and try again."

    # Generic exception - provide safe message
    # In production, we might want to hide technical details
    is_dev = os.getenv("ENVIRONMENT", "development").lower() == "development"

    if is_dev:
        # In development, show full error for debugging
        return f"Error during {context}: {error_type}: {error_msg}" if context else f"{error_type}: {error_msg}"
    else:
        # In production, hide technical details
        return (
            f"An error occurred during {context}. " "Please try again or contact support if the problem persists."
            if context
            else "An internal error occurred. Please try again or contact support if the problem persists."
        )
