# ADK-Ollama-AgentHub

A local, production-oriented AI agent framework built with **Google ADK**, **LiteLLM**, **Ollama**, and **Qwen3 8B**.

The project provides:

- Google ADK agent orchestration
- Local LLM execution through Ollama
- LiteLLM-based model integration
- Root-agent and specialist-agent delegation
- General calculation/system/date tools
- Generic bounded HTTP API tools
- MCP-based local tool integration
- FastAPI HTTP API
- SQLite-backed persistent ADK sessions
- In-memory ADK agent memory
- Guardrails and callbacks
- Structured application errors
- Unit and integration testing
- Logging and runtime diagnostics

---

## 1. Project Status

The following implementation phases have been completed and verified:

| Phase | Area | Status |
|---|---|---|
| Phase 6 | API tools | Complete |
| Phase 7 | MCP integration | Complete |
| Phase 8 | Multi-agent architecture | Complete |
| Phase 9 | FastAPI API | Complete |
| Phase 10 | SQLite-backed ADK sessions | Complete |
| Phase 11 | Project/configuration audit | In progress |

The project has been developed incrementally with explicit scope control.

Git setup is intentionally deferred until the project work is complete.

---

# 2. Architecture

## 2.1 High-level architecture

```text
                         User / Client
                              |
                              v
                         FastAPI API
                              |
                              v
                        AgentRunner
                              |
                              v
                         Root Agent
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
       General Agent      API Agent       MCP Agent
              |               |               |
              v               v               v
        Local Tools       HTTP Tools       MCP Toolset
                                              |
                                              v
                                        Local MCP Server

                              |
                              v
                     Google ADK Runner
                              |
                              v
                        Ollama / Qwen3
```

## 2.2 Persistence architecture

```text
FastAPI
   |
   v
AgentRunner
   |
   +----> SessionManager
   |          |
   |          v
   |   DatabaseSessionService
   |          |
   |          v
   |   SQLite: data/adk_sessions.db
   |
   +----> AgentMemory
              |
              v
      InMemoryMemoryService
```

### Important distinction

**Sessions are persistent. Memory is intentionally in-memory.**

SQLite persistence does not mean that the ADK memory service is persistent.

The application currently uses:

- `DatabaseSessionService` for persistent sessions
- `InMemoryMemoryService` for agent memory

---

# 3. Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| Python | 3.13.3 verified |
| Agent framework | Google ADK 2.8.0 |
| LLM integration | LiteLLM |
| Local model server | Ollama |
| Model | Qwen3 8B |
| API framework | FastAPI 0.141.1 |
| ASGI server | Uvicorn 0.52.4 |
| Validation | Pydantic 2.13.5 |
| Database | SQLite |
| ADK persistence | DatabaseSessionService |
| Async DB driver | aiosqlite 0.22.1 |
| ORM/database layer | SQLAlchemy 2.0.52 |
| MCP | MCP 1.29.1 |
| Testing | pytest / pytest-asyncio |
| Configuration | environment variables / YAML |
| Logging | Python logging |

---

# 4. Verified Runtime

The currently verified environment is:

```text
Python       3.13.3
google-adk  2.8.0
FastAPI      0.141.1
Uvicorn      0.52.4
Pydantic     2.13.5
SQLAlchemy   2.0.52
aiosqlite    0.22.1
MCP          1.29.1
Ollama model qwen3:8b
```

These versions describe the verified development environment. The dependency file should be used for installation rather than assuming every transitive package version is fixed.

---

# 5. Prerequisites

Before running the project, install/configure:

1. Windows
2. Python 3.13+
3. Ollama
4. Qwen3 8B model
5. PowerShell
6. Git is optional for now and intentionally deferred

Verify Python:

```powershell
python --version
```

Expected verified version:

```text
Python 3.13.3
```

Verify Ollama:

```powershell
ollama --version
```

---

# 6. Project Location

The verified development project is located at:

```text
D:\ADK-Ollama-AgentHub\ADK-Ollama-AgentHub
```

All commands in this README assume the terminal is opened in the project root.

```powershell
cd D:\ADK-Ollama-AgentHub\ADK-Ollama-AgentHub
```

---

# 7. Project Structure

```text
ADK-Ollama-AgentHub/
|
+-- app/
|   +-- agents/
|   |   +-- root_agent.py
|   |   +-- mcp_toolset.py
|   |   +-- sub_agents/
|   |       +-- general_agent.py
|   |       +-- api_agent.py
|   |       +-- mcp_agent.py
|   |
|   +-- api/
|   |   +-- main.py
|   |   +-- dependencies.py
|   |   +-- models.py
|   |   +-- routes/
|   |       +-- agent.py
|   |       +-- health.py
|   |       +-- sessions.py
|   |
|   +-- callbacks/
|   |   +-- callbacks.py
|   |   +-- guardrails.py
|   |   +-- logging_callbacks.py
|   |   +-- metrics.py
|   |
|   +-- memory/
|   |   +-- memory_service.py
|   |
|   +-- mcp/
|   |   +-- server.py
|   |   +-- mcp_client.py
|   |   +-- mcp_config.py
|   |   +-- mcp_manager.py
|   |
|   +-- services/
|   |   +-- agent_runner.py
|   |   +-- session_service.py
|   |   +-- services.py
|   |
|   +-- tools/
|   |   +-- function_tools.py
|   |   +-- api_tools.py
|   |   +-- file_tools.py
|   |
|   +-- utils/
|   |   +-- helpers.py
|   |   +-- logger.py
|   |
|   +-- workflows/
|       +-- workflows.py
|
+-- config/
|   +-- .env
|   +-- .env.example
|   +-- settings.yaml
|
+-- data/
|   +-- adk_sessions.db
|
+-- docs/
|   +-- PHASE_6_CHANGELOG.md
|   +-- PHASE_7_CHANGELOG.md
|   +-- PHASE_8_CHANGELOG.md
|   +-- PHASE_9_CHANGELOG.md
|   +-- PHASE_10_CHANGELOG.md
|
+-- logs/
|   +-- agent.log
|
+-- scripts/
|
+-- tests/
|   +-- unit/
|   +-- integration/
|   +-- e2e/
|
+-- .env
+-- .gitignore
+-- base_agent_source.txt
+-- pyproject.toml
+-- README.md
+-- requirements.txt
+-- run.py
```

Runtime-generated directories/files such as `.venv`, `.pytest_cache`, `__pycache__`, and local database/log artifacts may also exist.

---

# 8. Create the Virtual Environment

From the project root:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Confirm:

```powershell
python --version
```

The prompt should show:

```text
(.venv)
```

If PowerShell blocks activation, use the appropriate execution-policy configuration permitted by your environment. Do not disable security controls unnecessarily.

---

# 9. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

---

# 10. Install Dependencies

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

The primary dependencies include:

```text
google-adk
litellm
python-dotenv
pydantic
pyyaml
pytest
pytest-asyncio
fastapi
uvicorn
sqlalchemy
aiosqlite
mcp
```

Do not install unrelated database drivers unless the project scope explicitly requires them.

For the current SQLite implementation:

- `sqlalchemy` is required
- `aiosqlite` is required
- `asyncpg` is not required

---

# 11. Ollama Setup

Ollama provides the local LLM runtime.

Start Ollama if it is not already running:

```powershell
ollama serve
```

Check installed models:

```powershell
ollama list
```

Pull the verified model:

```powershell
ollama pull qwen3:8b
```

Verify:

```powershell
ollama list
```

You should see:

```text
qwen3:8b
```

The configured Ollama endpoint is:

```text
http://localhost:11434
```

---

# 12. Ollama API Verification

Verify that Ollama is reachable:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

The response should contain the installed model information.

If Ollama is unavailable, the application will not be able to perform local LLM execution.

---

# 13. Environment Configuration

The application uses environment-based configuration.

The expected core configuration is:

```dotenv
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
APP_NAME=adk_ollama_agent
LOG_LEVEL=INFO
```

Do not commit secrets, credentials, tokens, or machine-specific sensitive values.

Do not replace or modify existing environment configuration unless the change is explicitly required.

The repository currently contains configuration files in multiple locations. Treat the existing project configuration as authoritative and inspect the application's configuration loading behavior before consolidating or moving files.

---

# 14. YAML Configuration

The repository also contains:

```text
config/settings.yaml
```

This file is part of the project configuration area.

Environment variables and YAML configuration should not be assumed to be interchangeable. Changes to configuration precedence should be made deliberately.

---

# 15. `pyproject.toml`

`pyproject.toml` provides project/build metadata and pytest configuration.

The project uses pytest configuration from this file.

The test configuration includes the `tests` directory and asynchronous test support.

---

# 16. Database and Session Persistence

The application uses Google ADK:

```text
DatabaseSessionService
```

with:

```text
SQLite
+
SQLAlchemy async engine
+
aiosqlite
```

The application database is:

```text
data/adk_sessions.db
```

The database directory is created automatically when the session service module initializes.

The FastAPI application initializes the ADK database tables during application startup.

Conceptually:

```text
FastAPI lifespan startup
        |
        v
SessionManager.initialize()
        |
        v
DatabaseSessionService.prepare_tables()
```

At application shutdown, the database service is closed.

---

# 17. Session Persistence vs Memory

This project intentionally separates session persistence and agent memory.

## Persistent session storage

```text
data/adk_sessions.db
```

Stores ADK session information using `DatabaseSessionService`.

## Agent memory

The application currently uses:

```text
InMemoryMemoryService
```

Therefore:

- Sessions survive application/service recreation.
- Agent memory is not persistent across application restarts.
- SQLite session persistence does not automatically make memory persistent.

This separation is intentional.

---

# 18. Running the FastAPI Application

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

From the project root:

```powershell
uvicorn app.api.main:app --reload
```

The FastAPI service is normally available at:

```text
http://127.0.0.1:8000
```

---

# 19. FastAPI Swagger UI

When FastAPI is running, open:

```text
http://127.0.0.1:8000/docs
```

This provides interactive Swagger/OpenAPI documentation.

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

OpenAPI schema:

```text
http://127.0.0.1:8000/openapi.json
```

---

# 20. Health Endpoint

Endpoint:

```text
GET /health
```

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

The endpoint verifies that the application is running and returns the configured application information.

---

# 21. Session API

## Create a session

```text
POST /sessions
```

Example request:

```json
{
  "user_id": "user-1",
  "session_id": "session-1"
}
```

The exact request model is defined by:

```text
app/api/models.py
```

The API validates requests using Pydantic.

---

## Retrieve a session

```text
GET /sessions/{session_id}
```

The request uses the required user/session context.

---

# 22. Agent Message API

Endpoint:

```text
POST /sessions/{session_id}/messages
```

Example request:

```json
{
  "user_id": "user-1",
  "message": "What is 25 multiplied by 4?"
}
```

The API:

1. Validates the request.
2. Confirms the session exists.
3. Passes the request to `AgentRunner`.
4. Executes the ADK agent.
5. Collects execution events.
6. Returns a structured response.

---

# 23. API Request Validation

The API uses Pydantic models with strict validation.

The message input is bounded and cannot exceed the configured maximum.

Invalid requests return HTTP validation errors.

The API uses structured application errors for application-level failures.

---

# 24. Multi-Agent Architecture

The root agent is responsible for orchestration.

Specialist agents handle specific domains.

```text
root_agent
    |
    +-- general_agent
    |      |
    |      +-- calculate
    |      +-- system status
    |      +-- current datetime
    |
    +-- api_agent
    |      |
    |      +-- HTTP API tools
    |
    +-- mcp_agent
           |
           +-- MCP Toolset
```

The root agent delegates to the appropriate specialist.

Specialist agents are configured to prevent inappropriate peer-to-peer delegation where required by the architecture.

---

# 25. General Agent

The general agent handles general-purpose operations such as:

- Mathematical calculations
- System status
- Current date/time
- General conversational requests

The calculation tool uses AST-based validation rather than unrestricted Python `eval()`.

Supported arithmetic operations include:

```text
+
-
*
/
%
**
unary +
unary -
```

Unsafe expressions and unsupported AST nodes are rejected.

---

# 26. API Agent

The API agent handles HTTP/API-related operations.

The API tool implementation supports bounded:

```text
GET
POST
PUT
PATCH
DELETE
```

The implementation includes input and response limits and safe error handling.

Do not use the HTTP tool as an unrestricted arbitrary-network execution mechanism.

---

# 27. MCP Integration

The project includes Model Context Protocol integration.

The local MCP server is implemented in:

```text
app/mcp/server.py
```

The ADK MCP toolset is connected through:

```text
app/agents/mcp_toolset.py
```

The MCP specialist agent is:

```text
app/agents/sub_agents/mcp_agent.py
```

---

# 28. MCP Server

The current local MCP server uses:

```text
Host: 127.0.0.1
Port: 8000
Transport: Streamable HTTP
Path: /mcp
```

Endpoint:

```text
http://127.0.0.1:8000/mcp
```

The MCP server exposes these tools:

```text
mcp_health
get_server_time
add_numbers
multiply_numbers
```

---

# 29. Starting the MCP Server

From the project root:

```powershell
python -m app.mcp.server
```

The MCP server must be reachable before MCP integration tests or MCP-agent execution that depends on the server are attempted.

---

# 30. Important Port 8000 Limitation

**Important:**

The current project configuration uses port `8000` for both:

```text
FastAPI
```

and:

```text
MCP server
```

Two independent processes cannot simultaneously bind to the same:

```text
127.0.0.1:8000
```

Therefore, do not start both independent services on the same host/port at the same time.

For MCP integration testing, the MCP server must be available at:

```text
http://127.0.0.1:8000/mcp
```

If FastAPI is also required simultaneously, the port configuration must be intentionally separated before doing so.

Do not silently change the ports.

---

# 31. MCP Verification

With the MCP server running, verify the integration tests:

```powershell
pytest -q tests/integration/test_mcp_integration.py
```

Verify direct MCP tool invocation:

```powershell
pytest -q tests/integration/test_mcp_tool_invocation.py
```

Verify multi-agent MCP delegation:

```powershell
pytest -q tests/integration/test_multi_agent_delegation.py
```

MCP-related tests can fail with connection errors when the MCP server is not running.

A typical failure is:

```text
ConnectionError:
Failed to create MCP session:
All connection attempts failed
```

This indicates MCP connectivity should be checked before assuming the agent implementation is broken.

---

# 32. ADK Development Entry Point

The project also contains:

```text
run.py
```

This file is associated with the ADK development workflow.

For ADK development UI usage, run the ADK command appropriate to the installed Google ADK version and project layout.

Example:

```powershell
adk web
```

ADK development UI behavior and port usage are separate from the FastAPI API workflow.

On Windows, avoid assuming that every Unix-style `--reload` behavior is supported identically by the ADK development server.

---

# 33. Testing

The project contains:

```text
tests/
├── unit/
├── integration/
└── e2e/
```

Run the complete suite:

```powershell
pytest -q
```

Run unit tests:

```powershell
pytest -q tests/unit
```

Run integration tests:

```powershell
pytest -q tests/integration
```

Run end-to-end tests:

```powershell
pytest -q tests/e2e
```

Run a specific test:

```powershell
pytest -q tests/unit/test_tools.py
```

Run a specific integration test:

```powershell
pytest -q tests/integration/test_agent_memory.py
```

---

# 34. Test Categories

The test suite covers areas including:

- Agent execution
- Agent execution errors
- API endpoints
- API tools
- Callbacks
- Guardrails
- MCP manager
- MCP server
- MCP integration
- Memory service
- Metrics
- Multi-agent delegation
- Session persistence
- Session service
- Tool behavior

---

# 35. Verified Regression

The latest recorded full regression after Phase 10 persistence work was:

```text
167 passed, 18 warnings
```

Result:

```text
0 failures
```

MCP integration tests require the MCP server to be available.

Earlier test runs that occurred without the MCP server showed MCP connection failures. Once the MCP server was running, the MCP-related tests passed.

Do not treat a test run performed without required external/local services as a complete regression result.

---

# 36. Session Persistence Tests

The persistence implementation has focused tests that verify:

1. A session can be created.
2. Session state is stored.
3. The service can be closed.
4. A second service instance can reopen the database.
5. The session can be restored.
6. Session state is preserved.
7. Session deletion persists.

The database used for tests is isolated using temporary SQLite databases.

---

# 37. Memory Tests

Memory tests verify the ADK memory boundary and agent conversation retrieval behavior.

The current memory implementation is intentionally:

```text
InMemoryMemoryService
```

Therefore memory persistence across process restarts is not part of the current architecture.

---

# 38. Guardrails and Callbacks

Callback-related code is located under:

```text
app/callbacks/
```

Important components include:

```text
callbacks.py
guardrails.py
logging_callbacks.py
metrics.py
```

These components support:

- Input validation
- Guardrail enforcement
- Logging
- Execution-related metrics/hooks

Guardrails are intended to reject invalid or unsafe application requests before inappropriate execution occurs.

---

# 39. Structured Errors

Application errors are defined in:

```text
app/errors.py
```

The application includes error types such as:

```text
ApplicationError
ConfigurationError
SessionError
AgentExecutionError
ToolExecutionError
```

Application errors expose structured error information.

Do not expose internal exception traces or sensitive implementation details through public API responses.

---

# 40. Logging

Application logging is implemented under:

```text
app/utils/logger.py
```

Runtime logs are written under:

```text
logs/
```

The primary current log file is:

```text
logs/agent.log
```

Logging is intended to provide useful operational information without exposing secrets.

---

# 41. Runtime Artifacts

The project may generate local runtime artifacts such as:

```text
.venv/
.pytest_cache/
__pycache__/
data/adk_sessions.db
logs/agent.log
app/.adk/
```

These should be treated differently from source files.

The SQLite database is an application runtime artifact.

The log file is an application runtime artifact.

Python bytecode and pytest caches are generated artifacts.

Do not manually modify runtime databases unless you understand the consequences.

---

# 42. `.adk` Directory

The project has an ADK-related runtime directory under:

```text
app/.adk/
```

A session database has been observed there during development.

The application-level persistent session database introduced in Phase 10 is:

```text
data/adk_sessions.db
```

Do not delete or consolidate ADK runtime files merely because they appear duplicated without first determining which component created them.

---

# 43. Configuration Files

Current project configuration areas include:

```text
.env
app/.env
config/.env
config/.env.example
config/settings.yaml
```

Because multiple environment files exist in the current development tree, configuration precedence must be understood before making cleanup/consolidation changes.

Do not assume all `.env` files are loaded simultaneously.

The application's actual configuration-loading behavior should be treated as authoritative.

---

# 44. Security Guidelines

## Secrets

Never commit:

- API keys
- Passwords
- Access tokens
- OAuth secrets
- Cloud credentials
- Private certificates
- Machine-specific credentials

## Local configuration

Use environment configuration for sensitive/local values.

## HTTP tools

HTTP tools are bounded and should not be expanded into unrestricted network execution without explicit security review.

## MCP

The current MCP server binds to:

```text
127.0.0.1
```

This is intentionally local.

Do not expose the MCP server publicly without authentication, authorization, network controls, and an explicit security review.

## Input validation

Maintain the existing input limits and Pydantic validation.

---

# 45. Troubleshooting

## Ollama connection failure

Check:

```powershell
ollama list
```

Check the Ollama API:

```powershell
Invoke-RestMethod http://localhost:11434/api/tags
```

If the model is missing:

```powershell
ollama pull qwen3:8b
```

---

## MCP connection failure

Typical error:

```text
Failed to create MCP session:
All connection attempts failed
```

Check whether the MCP server is running.

Start it:

```powershell
python -m app.mcp.server
```

Check the configured endpoint:

```text
http://127.0.0.1:8000/mcp
```

---

## Port 8000 already in use

Check the process using the port:

```powershell
Get-NetTCPConnection -LocalPort 8000
```

The current project uses port 8000 for local services, so identify which service owns it before stopping anything.

Do not randomly terminate processes.

---

## FastAPI does not start

Verify:

```powershell
python --version
```

Verify the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify dependencies:

```powershell
pip install -r requirements.txt
```

Then retry:

```powershell
uvicorn app.api.main:app --reload
```

---

## Database initialization problems

Check:

```text
data/adk_sessions.db
```

The application should initialize the ADK database schema during FastAPI startup.

Do not manually delete the database unless you intentionally want to remove local session data.

---

## Tests fail because MCP is unavailable

Run MCP-dependent tests only after the local MCP server is available.

The following tests are MCP-dependent:

```text
test_mcp_integration.py
test_mcp_tool_invocation.py
test_multi_agent_delegation.py
```

---

# 46. Useful Verification Commands

## Python

```powershell
python --version
```

## Installed ADK

```powershell
python -c "import google.adk; print(getattr(google.adk, '__version__', 'version attribute unavailable'))"
```

## FastAPI

```powershell
python -c "import fastapi; print(fastapi.__version__)"
```

## Uvicorn

```powershell
python -c "import uvicorn; print(uvicorn.__version__)"
```

## Pydantic

```powershell
python -c "import pydantic; print(pydantic.__version__)"
```

## SQLAlchemy

```powershell
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
```

## aiosqlite

```powershell
python -c "import aiosqlite; print(aiosqlite.__version__)"
```

## MCP

```powershell
python -c "import mcp; print(getattr(mcp, '__version__', 'version attribute unavailable'))"
```

## Ollama model

```powershell
ollama list
```

## Database

```powershell
Test-Path .\data\adk_sessions.db
```

## Tests

```powershell
pytest -q
```

---

# 47. Daily Development Workflow

A typical development session:

### Terminal 1 — Ollama

```powershell
ollama serve
```

### Terminal 2 — MCP when MCP testing is required

```powershell
.\.venv\Scripts\Activate.ps1
python -m app.mcp.server
```

### Terminal 3 — API when API testing is required

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.api.main:app --reload
```

Remember the current port-8000 conflict. These services cannot all independently bind to the same port simultaneously under the current configuration.

---

# 48. Fresh Project Setup

For a new development environment:

```powershell
cd D:\ADK-Ollama-AgentHub\ADK-Ollama-AgentHub

python -m venv .venv

.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

pip install -r requirements.txt

ollama pull qwen3:8b

python -m pytest -q
```

If MCP integration tests are included in the test run, ensure the required MCP server is available.

---

# 49. Quick Start

Minimum API startup:

```powershell
cd D:\ADK-Ollama-AgentHub\ADK-Ollama-AgentHub

.\.venv\Scripts\Activate.ps1

uvicorn app.api.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
http://127.0.0.1:8000/health
```

---

# 50. API Endpoint Summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health |
| POST | `/sessions` | Create session |
| GET | `/sessions/{session_id}` | Retrieve session |
| POST | `/sessions/{session_id}/messages` | Execute agent message |
| GET | `/docs` | Swagger UI |
| GET | `/redoc` | ReDoc |
| GET | `/openapi.json` | OpenAPI schema |

---

# 51. Important Source Locations

## Root agent

```text
app/agents/root_agent.py
```

## Specialist agents

```text
app/agents/sub_agents/
```

## Agent runner

```text
app/services/agent_runner.py
```

## Session service

```text
app/services/session_service.py
```

## Memory

```text
app/memory/memory_service.py
```

## FastAPI application

```text
app/api/main.py
```

## API routes

```text
app/api/routes/
```

## API models

```text
app/api/models.py
```

## MCP server

```text
app/mcp/server.py
```

## MCP toolset

```text
app/agents/mcp_toolset.py
```

## Tools

```text
app/tools/
```

## Callbacks

```text
app/callbacks/
```

## Configuration

```text
app/config.py
config/
.env
```

## Logging

```text
app/utils/logger.py
logs/
```

---

# 52. Phase Documentation

Phase-specific implementation notes are maintained under:

```text
docs/
```

Current changelogs include:

```text
docs/PHASE_6_CHANGELOG.md
docs/PHASE_7_CHANGELOG.md
docs/PHASE_8_CHANGELOG.md
docs/PHASE_9_CHANGELOG.md
docs/PHASE_10_CHANGELOG.md
```

These documents provide implementation-specific history and verification details.

---

# 53. Phase 6 — API Tools

Phase 6 introduced bounded generic HTTP API tools.

Implemented capabilities include:

```text
GET
POST
PUT
PATCH
DELETE
```

The implementation includes limits and safe error handling.

---

# 54. Phase 7 — MCP

Phase 7 introduced local MCP integration.

Implemented:

- MCP server
- Streamable HTTP transport
- MCP toolset
- MCP client/manager components
- MCP integration tests
- Direct MCP tool invocation tests

The MCP server provides:

```text
mcp_health
get_server_time
add_numbers
multiply_numbers
```

---

# 55. Phase 8 — Multi-Agent Architecture

Phase 8 introduced:

```text
root_agent
general_agent
api_agent
mcp_agent
```

The root agent delegates requests to specialist agents.

The architecture uses ADK agent-to-agent transfer capabilities.

The root agent does not directly own the specialist domain tools.

---

# 56. Phase 9 — FastAPI

Phase 9 introduced:

- FastAPI application
- Health endpoint
- Session APIs
- Agent execution API
- Pydantic models
- Structured API errors
- Service boundary
- Session-aware execution
- API tests

Verified endpoints:

```text
/health
/sessions
/sessions/{session_id}
/sessions/{session_id}/messages
```

---

# 57. Phase 10 — Persistent ADK Sessions

Phase 10 introduced persistent ADK sessions using:

```text
DatabaseSessionService
```

with:

```text
SQLite
SQLAlchemy
aiosqlite
```

Database:

```text
data/adk_sessions.db
```

Verified:

- Database initialization
- Session creation
- Session persistence across service instances
- Session state restoration
- Session deletion persistence
- API compatibility
- Full regression

Recorded regression:

```text
167 passed, 18 warnings
0 failures
```

Agent memory remained intentionally in-memory.

---

# 58. Scope Boundaries

The following are intentionally outside the current implemented scope unless explicitly approved:

- PostgreSQL
- `asyncpg`
- Redis
- Persistent ADK memory
- OAuth/JWT
- Prometheus
- OpenTelemetry
- Docker
- Kubernetes
- Cloud deployment
- Git setup
- Additional LLM providers
- Unapproved port changes
- Unapproved environment-file consolidation

These should not be assumed to be implemented merely because the architecture could support them in the future.

---

# 59. Development Principles

The project follows these principles:

1. Keep clear application/service boundaries.
2. Validate external inputs.
3. Avoid unrestricted code execution.
4. Keep local model execution explicit.
5. Keep MCP integration local unless explicitly secured.
6. Separate persistent sessions from memory.
7. Keep configuration externalized.
8. Keep tests close to the implementation they verify.
9. Record phase-specific implementation changes.
10. Avoid unrelated architecture changes during scoped implementation work.

---

# 60. Production Readiness Considerations

The current project has a strong local development and test architecture, but production deployment requires additional controls.

Before production deployment, evaluate:

- Authentication
- Authorization
- TLS
- Secret management
- Network isolation
- Rate limiting
- Persistent memory requirements
- Database backup
- Database concurrency
- Observability
- Centralized logging
- Metrics
- Distributed deployment
- Containerization
- Health/readiness probes
- Resource limits
- Model serving capacity
- MCP authentication
- API security
- Dependency vulnerability scanning

These are considerations, not claims that the features are already implemented.

---

# 61. Known Warnings

The test suite may report warnings originating from dependencies.

Examples include:

- ADK experimental feature warnings
- ADK deprecation warnings
- MCP-related experimental/deprecation warnings
- Starlette/AnyIO dependency warnings

A warning is not equivalent to a test failure.

The recorded Phase 10 regression completed with:

```text
167 passed, 18 warnings
```

---

# 62. No Silent Architecture Changes

This README documents the current verified architecture.

Do not infer that an item is implemented simply because it is described as a future consideration.

In particular:

```text
Persistent session != persistent memory
```

and:

```text
FastAPI != MCP server
```

They are separate application components.

---

# 63. License

No final open-source license has been selected for this project at the current stage.

Do not assume a license or redistribute the project under a specific license without an explicit decision.

---

# 64. Final Project Verification Checklist

Before considering a local environment ready, verify:

```text
[ ] Python 3.13+ installed
[ ] Virtual environment created
[ ] Virtual environment activated
[ ] Dependencies installed
[ ] Ollama installed
[ ] Ollama service running
[ ] qwen3:8b available
[ ] Environment configuration available
[ ] FastAPI starts successfully
[ ] /health responds successfully
[ ] Swagger UI opens
[ ] Session can be created
[ ] Session can be retrieved
[ ] Agent message can execute
[ ] SQLite database exists
[ ] MCP server starts when required
[ ] MCP endpoint is reachable when required
[ ] MCP integration tests pass when server is running
[ ] Unit tests pass
[ ] Integration tests pass
[ ] Full regression passes
```

---

# 65. Verified Current State

The project currently has:

- Local Ollama/Qwen3 execution
- Google ADK orchestration
- LiteLLM model integration
- Multi-agent delegation
- General tools
- API tools
- MCP tools
- FastAPI API
- SQLite-backed ADK session persistence
- In-memory ADK memory
- Guardrails
- Callbacks
- Structured errors
- Logging
- Unit/integration testing
- Phase-specific documentation

The most recent recorded full regression after the persistent-session implementation was:

```text
167 passed, 18 warnings
0 failures
```

This README documents the current implementation and its verified boundaries without claiming that deferred production features are already implemented.
