# RUN_FASTAPI.md

# Running the FastAPI Application

This guide explains how to start the FastAPI application for **ADK-Ollama-AgentHub**, verify that it is running, create a session, send a question to the configured Qwen3 model, and stop the server.

## 1. Prerequisites

Run all commands from the project root:

```powershell
cd D:\ADK-Ollama-AgentHub\ADK-Ollama-AgentHub
```

Activate the Python virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Verify Python:

```powershell
python --version
```

The project is configured to use:

- FastAPI
- Uvicorn
- Google ADK
- LiteLLM
- Ollama
- Qwen3 8B

Make sure Ollama is running and the configured model is available:

```powershell
ollama list
```

Expected model:

```text
qwen3:8b
```

Do not modify `.env` for normal execution.

---

## 2. Start FastAPI

From the project root, run:

```powershell
uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

Expected output is similar to:

```text
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Keep this PowerShell window running.

> **Important:** Port `8000` is also used by the local MCP server. Do not run the FastAPI server and MCP server on the same port at the same time.

---

## 3. Check the Health Endpoint

Open another PowerShell window.

Run:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/health"
```

Expected result:

```text
status
------
healthy
```

This confirms that the FastAPI application is running.

---

## 4. View OpenAPI Documentation

Open the following URL in a browser:

```text
http://127.0.0.1:8000/docs
```

FastAPI Swagger UI should be displayed.

The API currently exposes these main endpoints:

```text
GET    /health
POST   /sessions
GET    /sessions/{session_id}
POST   /sessions/{session_id}/messages
```

---

## 5. Create a Session

Create a session before sending a message.

PowerShell:

```powershell
$session = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/sessions" `
  -ContentType "application/json" `
  -Body '{"user_id":"api-test-user"}'
```

Display the response:

```powershell
$session | ConvertTo-Json -Depth 20
```

The response contains a `session_id`.

Store it:

```powershell
$sessionId = $session.session_id
```

Verify:

```powershell
$sessionId
```

---

## 6. Send a Question to the LLM

Use the session ID created above.

Example:

```powershell
$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/sessions/$sessionId/messages?user_id=api-test-user" `
  -ContentType "application/json" `
  -Body '{"message":"What is law?"}'
```

Display the response:

```powershell
$response | ConvertTo-Json -Depth 50
```

The response contains the ADK execution events.

---

## 7. What to Verify in the Response

For a successful LLM request, verify the following:

### Model

The model should be:

```text
ollama_chat/qwen3:8b
```

### Author

The response should identify the specialist agent that handled the request, for example:

```text
general_agent
```

### Answer

The final non-thought content should contain the model's answer.

For the example question:

```text
What is law?
```

the answer should explain the concept of law.

### Errors

Execution metrics should show:

```text
model_errors: 0
tool_errors: 0
```

A successful request therefore demonstrates:

```text
FastAPI
   ↓
ADK
   ↓
Agent
   ↓
LiteLLM
   ↓
Ollama
   ↓
Qwen3 8B
```

---

## 8. Complete Example

The following sequence can be copied into a second PowerShell window while the FastAPI server is running.

### Step 1 — Health

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/health"
```

### Step 2 — Create Session

```powershell
$session = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/sessions" `
  -ContentType "application/json" `
  -Body '{"user_id":"api-test-user"}'

$session | ConvertTo-Json -Depth 20

$sessionId = $session.session_id
```

### Step 3 — Ask Question

```powershell
$response = Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/sessions/$sessionId/messages?user_id=api-test-user" `
  -ContentType "application/json" `
  -Body '{"message":"What is law?"}'
```

### Step 4 — Inspect Response

```powershell
$response | ConvertTo-Json -Depth 50
```

---

## 9. Run the API LLM Integration Test

The project includes an integration test that validates the API → ADK → Ollama/Qwen3 flow.

Run:

```powershell
pytest -q tests/integration/test_api_llm_answer.py -s --question "What is law?"
```

Expected successful result is similar to:

```text
======================================================================
API LLM ANSWER TEST
======================================================================

Question:
What is law?

Model:
ollama_chat/qwen3:8b

Author:
general_agent

Answer:
Law is a system of rules and guidelines established by a government
or authority to regulate behavior, maintain order, and resolve disputes
within a society.

Model errors:
0

Tool errors:
0

======================================================================
.
1 passed
```

The exact answer text may differ because it is generated by the LLM.

---

## 10. Run the Full API/E2E Tests

For the API end-to-end tests:

```powershell
pytest -q tests/e2e -s
```

For the full project regression suite:

```powershell
pytest -q
```

The full suite may take several minutes because it includes LLM-backed tests.

---

## 11. Common Issues

### Port 8000 is already in use

Check which process is using port 8000:

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

The most common cause in this project is that the MCP server is already running.

Stop the existing server with:

```text
Ctrl+C
```

Then start FastAPI again:

```powershell
uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

### Ollama is not available

Check:

```powershell
ollama list
```

The expected model is:

```text
qwen3:8b
```

Also verify Ollama itself is running.

### Health works but the LLM request fails

Check the FastAPI terminal for the application error.

Also verify the configured Ollama endpoint and model. The project configuration uses:

```text
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

Do not change `.env` unless there is an approved configuration change.

### Session creation returns an error

The successful session creation status is:

```text
201 Created
```

Do not expect `200` for `POST /sessions`.

### Message request returns an error

Make sure:

1. FastAPI is running.
2. The session was created successfully.
3. The `session_id` is correct.
4. The `user_id` in the query string matches the user used to create the session.
5. The request body contains `message`.

Correct format:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/sessions/$sessionId/messages?user_id=api-test-user" `
  -ContentType "application/json" `
  -Body '{"message":"What is law?"}'
```

---

## 12. FastAPI vs MCP

This project has separate execution paths.

### FastAPI / ADK

```text
Client
  ↓
FastAPI
  ↓
ADK
  ↓
Root Agent / Specialist Agent
  ↓
LiteLLM
  ↓
Ollama
  ↓
Qwen3 8B
```

### Independent MCP LLM

```text
MCP Client
  ↓
MCP Server
  ↓
ask_question
  ↓
LiteLLM
  ↓
Ollama
  ↓
Qwen3 8B
```

The two paths are intentionally separate.

FastAPI uses the ADK agent architecture, sessions, routing, tools, and execution metrics.

MCP's `ask_question` tool provides independent LLM answering without going through the ADK root agent.

---

## 13. Stopping FastAPI

In the terminal where Uvicorn is running, press:

```text
Ctrl+C
```

Expected shutdown output is similar to:

```text
INFO:     Shutting down
INFO:     Finished server process
```

---

## 14. Recommended Verification Sequence

For a clean manual verification:

```text
1. Activate .venv
2. Verify Ollama and qwen3:8b
3. Start FastAPI
4. Check /health
5. Open /docs
6. Create a session
7. Send "What is law?"
8. Verify qwen3:8b
9. Verify answer content
10. Verify model_errors = 0
11. Verify tool_errors = 0
12. Stop FastAPI
```

This sequence validates the complete FastAPI LLM execution path without changing the project configuration.
