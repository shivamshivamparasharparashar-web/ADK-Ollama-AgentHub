# ADK Web UI Runner

## Start

``` powershell
cd D:\ADK-Ollama-AgentHub\ADK-Ollama-AgentHub
.venv\Scripts\Activate.ps1
adk web
```

Open the URL printed by `adk web`.

## Test

1.  Select `adk_ollama_agent`.
2.  Start a session.
3.  Send `What is 2 + 2?`.
4.  Verify the agent responds.
5.  Test a tool request such as `Calculate 15 * 7`.

## Important

Port `8000` is shared by ADK Web, MCP, and FastAPI in this project. Only
one may use it at a time.

If `/dev-ui/...` shows `Not Found`, check:

``` powershell
netstat -ano | findstr :8000
```

Stop MCP/FastAPI before running `adk web`.

## Stop

Press `Ctrl+C`.
