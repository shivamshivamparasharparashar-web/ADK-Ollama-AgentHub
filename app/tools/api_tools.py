from __future__ import annotations

import json
import socket
from http.client import HTTPException
from ipaddress import ip_address
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse, urlencode, urlunparse
from urllib.request import Request, urlopen

from app.errors import ToolExecutionError

MAX_URL_LENGTH = 2_048
MAX_BODY_LENGTH = 1_048_576
MIN_TIMEOUT_SECONDS = 1
MAX_TIMEOUT_SECONDS = 30
ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
SAFE_RESPONSE_HEADERS = {"content-type", "content-length", "etag", "last-modified"}


def _validate_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ToolExecutionError("API URL must be a non-empty string.")
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        raise ToolExecutionError("API URL exceeds the maximum allowed length.")

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ToolExecutionError("API URL must be a valid HTTP or HTTPS URL.")
    if parsed.username or parsed.password:
        raise ToolExecutionError("API URL must not contain embedded credentials.")
    return url


def _validate_timeout(timeout_seconds: float) -> float:
    try:
        timeout = float(timeout_seconds)
    except (TypeError, ValueError) as exc:
        raise ToolExecutionError("timeout_seconds must be a number.") from exc
    if not MIN_TIMEOUT_SECONDS <= timeout <= MAX_TIMEOUT_SECONDS:
        raise ToolExecutionError(
            f"timeout_seconds must be between {MIN_TIMEOUT_SECONDS} and {MAX_TIMEOUT_SECONDS}."
        )
    return timeout


def _validate_headers(headers: dict[str, str] | None) -> dict[str, str]:
    if headers is None:
        return {}
    if not isinstance(headers, dict):
        raise ToolExecutionError("headers must be a dictionary.")

    validated: dict[str, str] = {}
    for name, value in headers.items():
        if not isinstance(name, str) or not name.strip():
            raise ToolExecutionError("Header names must be non-empty strings.")
        if not isinstance(value, str):
            raise ToolExecutionError("Header values must be strings.")
        validated[name] = value
    return validated


def _build_url(url: str, query_params: dict[str, Any] | None) -> str:
    if query_params is None:
        return url
    if not isinstance(query_params, dict):
        raise ToolExecutionError("query_params must be a dictionary.")

    parsed = urlparse(url)
    encoded = urlencode(query_params, doseq=True)
    combined_query = f"{parsed.query}&{encoded}" if parsed.query and encoded else parsed.query or encoded
    result = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            combined_query,
            parsed.fragment,
        )
    )
    if len(result) > MAX_URL_LENGTH:
        raise ToolExecutionError("API URL exceeds the maximum allowed length.")
    return result


def _encode_body(json_body: Any | None) -> bytes | None:
    if json_body is None:
        return None
    try:
        encoded = json.dumps(json_body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ToolExecutionError("json_body must be JSON serializable.") from exc
    if len(encoded) > MAX_BODY_LENGTH:
        raise ToolExecutionError("Request body exceeds the maximum allowed size.")
    return encoded


def _safe_response_headers(headers: Any) -> dict[str, str]:
    return {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() in SAFE_RESPONSE_HEADERS
    }


def _decode_response(raw: bytes, content_type: str | None) -> Any:
    text = raw.decode("utf-8", errors="replace")
    if content_type and "json" in content_type.lower():
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return text


def api_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    query_params: dict[str, Any] | None = None,
    json_body: Any | None = None,
    timeout_seconds: float = 10,
) -> dict[str, Any]:
    """Perform a bounded HTTP API request and return a structured response."""
    if not isinstance(method, str):
        raise ToolExecutionError("HTTP method must be a string.")
    method = method.upper().strip()
    if method not in ALLOWED_METHODS:
        raise ToolExecutionError(
            f"HTTP method must be one of: {', '.join(sorted(ALLOWED_METHODS))}."
        )

    request_url = _build_url(_validate_url(url), query_params)
    request_headers = _validate_headers(headers)
    body = _encode_body(json_body)
    timeout = _validate_timeout(timeout_seconds)

    if body is not None and "Content-Type" not in request_headers and "content-type" not in request_headers:
        request_headers["Content-Type"] = "application/json"

    request = Request(
        request_url,
        data=body,
        headers=request_headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read(MAX_BODY_LENGTH + 1)
            if len(raw) > MAX_BODY_LENGTH:
                raise ToolExecutionError("API response exceeds the maximum allowed size.")
            content_type = response.headers.get("Content-Type")
            return {
                "ok": 200 <= response.status < 300,
                "status_code": response.status,
                "headers": _safe_response_headers(response.headers),
                "body": _decode_response(raw, content_type),
            }
    except HTTPError as exc:
        raw = exc.read(MAX_BODY_LENGTH + 1)
        if len(raw) > MAX_BODY_LENGTH:
            body_value: Any = "Response body exceeds the maximum allowed size."
        else:
            body_value = _decode_response(raw, exc.headers.get("Content-Type"))
        return {
            "ok": False,
            "status_code": exc.code,
            "headers": _safe_response_headers(exc.headers),
            "body": body_value,
        }
    except (URLError, TimeoutError, socket.timeout, HTTPException, OSError) as exc:
        raise ToolExecutionError(
            "API request failed.",
            details=type(exc).__name__,
        ) from exc


__all__ = ["api_request"]
