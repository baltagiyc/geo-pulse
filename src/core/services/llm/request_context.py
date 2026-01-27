"""Request-scoped context for sensitive API keys."""

from __future__ import annotations

import contextvars
from contextvars import Token

_openai_api_key_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("openai_api_key", default=None)
_google_api_key_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("google_api_key", default=None)


def set_request_api_keys(
    openai_api_key: str | None, google_api_key: str | None
) -> tuple[Token[str | None], Token[str | None]]:
    """Store API keys in a request-scoped context."""
    return (
        _openai_api_key_var.set(openai_api_key),
        _google_api_key_var.set(google_api_key),
    )


def reset_request_api_keys(tokens: tuple[Token[str | None], Token[str | None]]) -> None:
    """Reset request-scoped API keys to previous values."""
    openai_token, google_token = tokens
    _openai_api_key_var.reset(openai_token)
    _google_api_key_var.reset(google_token)


def get_request_api_keys() -> tuple[str | None, str | None]:
    """Return the current request-scoped API keys."""
    return _openai_api_key_var.get(), _google_api_key_var.get()
