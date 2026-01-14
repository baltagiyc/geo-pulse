"""Custom exception handlers for FastAPI."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


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

        # For other validation errors, return the default format
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": errors},
        )
