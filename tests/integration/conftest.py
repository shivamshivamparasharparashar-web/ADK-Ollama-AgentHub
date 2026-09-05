from __future__ import annotations


def pytest_addoption(parser):
    parser.addoption(
        "--question",
        action="store",
        default=None,
        help="Question to send to the API LLM.",
    )