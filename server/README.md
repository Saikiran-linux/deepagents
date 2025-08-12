Run the API server for DeepAgents UI
------------------------------------

Requirements:
- Python 3.10+
- `TAVILY_API_KEY` set in environment or project `.env`

Setup:

```
pip install -r server/requirements.txt
pip install -e .
python -m server.main
```

Environment:
- `FRONTEND_ORIGIN` (optional) defaults to `http://localhost:3000`
- `HOST` (optional) defaults to `0.0.0.0`
- `PORT` (optional) defaults to `8000`
- `RELOAD` (optional) defaults to `1`

Endpoints:
- `GET /api/agents` — list available agents
- `POST /api/agent/run` — run selected agent with a prompt
- `GET /health` — health check



