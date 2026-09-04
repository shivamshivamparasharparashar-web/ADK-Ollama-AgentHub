from google.adk.memory import InMemoryMemoryService

from app.config import settings


class AgentMemory:
    def __init__(self):
        self.service = InMemoryMemoryService()

    async def add_session_to_memory(self, session):
        await self.service.add_session_to_memory(session)

    async def search(
        self,
        user_id: str,
        query: str,
        app_name: str | None = None,
    ):
        return await self.service.search_memory(
            app_name=app_name or settings.APP_NAME,
            user_id=user_id,
            query=query,
        )


agent_memory = AgentMemory()