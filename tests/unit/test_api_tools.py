from __future__ import annotations

import json
from urllib.error import URLError

import pytest

from app.errors import ToolExecutionError
from app.tools.api_tools import api_request


def test_api_request_rejects_invalid_method():
    with pytest.raises(ToolExecutionError):
        api_request("TRACE", "https://example.com")


def test_api_request_rejects_invalid_url():
    with pytest.raises(ToolExecutionError):
        api_request("GET", "ftp://example.com")


def test_api_request_rejects_embedded_credentials():
    with pytest.raises(ToolExecutionError):
        api_request("GET", "https://user:password@example.com")


def test_api_request_rejects_invalid_timeout():
    with pytest.raises(ToolExecutionError):
        api_request("GET", "https://example.com", timeout_seconds=31)


def test_api_request_builds_json_request(monkeypatch):
    captured = {}

    class FakeResponse:
        status = 200
        headers = {"Content-Type": "application/json", "Set-Cookie": "secret"}

        def read(self, size):
            return json.dumps({"ok": True}).encode()

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("app.tools.api_tools.urlopen", fake_urlopen)

    result = api_request(
        "post",
        "https://example.com/api",
        headers={"Authorization": "Bearer secret"},
        query_params={"page": 2},
        json_body={"name": "agent"},
        timeout_seconds=5,
    )

    assert result["ok"] is True
    assert result["status_code"] == 200
    assert result["body"] == {"ok": True}
    assert "set-cookie" not in result["headers"]
    assert captured["timeout"] == 5.0
    assert captured["request"].method == "POST"
    assert captured["request"].full_url == "https://example.com/api?page=2"
    assert json.loads(captured["request"].data.decode()) == {"name": "agent"}


def test_api_request_returns_http_error_as_structured_result(monkeypatch):
    from io import BytesIO
    from urllib.error import HTTPError

    error = HTTPError(
        "https://example.com",
        404,
        "Not Found",
        {"Content-Type": "application/json"},
        BytesIO(b'{"error":"not found"}'),
    )

    def fake_urlopen(request, timeout):
        raise error

    monkeypatch.setattr("app.tools.api_tools.urlopen", fake_urlopen)

    result = api_request("GET", "https://example.com")

    assert result == {
        "ok": False,
        "status_code": 404,
        "headers": {"content-type": "application/json"},
        "body": {"error": "not found"},
    }


def test_api_request_normalizes_transport_error(monkeypatch):
    def fake_urlopen(request, timeout):
        raise URLError("internal connection detail")

    monkeypatch.setattr("app.tools.api_tools.urlopen", fake_urlopen)

    with pytest.raises(ToolExecutionError) as exc_info:
        api_request("GET", "https://example.com")

    assert str(exc_info.value) == "API request failed."
    assert exc_info.value.details == "URLError"
    assert "internal connection detail" not in str(exc_info.value)
