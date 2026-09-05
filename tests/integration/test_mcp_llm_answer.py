from __future__ import annotations

import argparse
import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_URL = "http://127.0.0.1:8000/mcp"


async def ask_mcp(question: str) -> dict:
    async with streamable_http_client(MCP_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                "ask_question",
                {"question": question},
            )

            if result.isError:
                raise RuntimeError(f"MCP tool returned an error: {result.content}")

            text_parts = [
                item.text
                for item in result.content
                if hasattr(item, "text") and item.text
            ]

            if not text_parts:
                raise RuntimeError("MCP returned no text content.")

            return json.loads("\n".join(text_parts))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ask a question through the independent MCP LLM."
    )
    parser.add_argument(
        "question",
        help="Question to send to the MCP ask_question tool.",
    )

    args = parser.parse_args()

    response = asyncio.run(ask_mcp(args.question))

    print("\nQuestion:")
    print(response["question"])

    print("\nModel:")
    print(response["model"])

    print("\nAnswer:")
    print(response["answer"])


if __name__ == "__main__":
    main()