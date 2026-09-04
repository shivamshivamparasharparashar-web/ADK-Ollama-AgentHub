from __future__ import annotations

from google.adk.runners import Runner
from google.genai import types

from app.config import settings
from app.errors import AgentExecutionError
from app.agents.root_agent import root_agent
from app.services.session_service import session_manager
from app.memory.memory_service import agent_memory
from app.utils.logger import logger


class AgentRunner:
    """Application-level wrapper around the Google ADK Runner."""

    def __init__(self) -> None:
        self.runner = Runner(
            agent=root_agent,
            app_name=settings.APP_NAME,
            session_service=session_manager.service,
        )

    async def create_session(
        self,
        user_id: str,
        session_id: str,
        state: dict | None = None,
    ):
        """Create an application session."""

        try:
            return await session_manager.create_session(
                app_name=settings.APP_NAME,
                user_id=user_id,
                session_id=session_id,
                state=state,
            )

        except Exception as exc:
            logger.exception(
                "Session creation failed "
                "error_type=%s",
                type(exc).__name__,
            )

            raise AgentExecutionError(
                "Session creation failed.",
                details=type(exc).__name__,
            ) from exc

    async def get_session(
        self,
        user_id: str,
        session_id: str,
    ):
        """Retrieve an application session."""

        try:
            return await session_manager.get_session(
                app_name=settings.APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )

        except Exception as exc:
            logger.exception(
                "Session retrieval failed "
                "error_type=%s",
                type(exc).__name__,
            )

            raise AgentExecutionError(
                "Session retrieval failed.",
                details=type(exc).__name__,
            ) from exc

    async def run(
        self,
        user_id: str,
        session_id: str,
        message: str,
    ):
        """
        Execute the agent and persist the resulting session to memory.

        User input and tool arguments are intentionally not logged.
        """

        new_message = types.Content(
            role="user",
            parts=[
                types.Part(text=message),
            ],
        )

        events = []

        try:
            logger.info(
                "Agent run started user_id=%s session_id=%s",
                user_id,
                session_id,
            )

            async for event in self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message,
            ):
                events.append(event)

            logger.info(
                "Agent execution completed "
                "user_id=%s session_id=%s events=%d",
                user_id,
                session_id,
                len(events),
            )

        except Exception as exc:
            # Keep the caller-facing error safe.
            #
            # The complete traceback is retained in the application log
            # for diagnosis, but the original exception message is not
            # returned to the caller.
            logger.exception(
                "Agent execution failed "
                "user_id=%s session_id=%s error_type=%s",
                user_id,
                session_id,
                type(exc).__name__,
            )

            raise AgentExecutionError(
                "Agent execution failed.",
                details=type(exc).__name__,
            ) from exc

        try:
            session = await self.get_session(
                user_id=user_id,
                session_id=session_id,
            )

            if session is not None:
                await agent_memory.add_session_to_memory(session)

                logger.info(
                    "Agent session added to memory "
                    "user_id=%s session_id=%s",
                    user_id,
                    session_id,
                )

        except Exception as exc:
            # Memory persistence is separated from agent execution so that
            # a memory failure cannot hide the fact that the agent itself
            # successfully completed.
            logger.exception(
                "Agent memory persistence failed "
                "user_id=%s session_id=%s error_type=%s",
                user_id,
                session_id,
                type(exc).__name__,
            )

            raise AgentExecutionError(
                "Agent memory persistence failed.",
                details=type(exc).__name__,
            ) from exc

        return events


agent_runner = AgentRunner()


__all__ = ["AgentRunner", "agent_runner"]