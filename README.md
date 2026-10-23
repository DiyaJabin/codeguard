# CodeGuard AI

CodeGuard AI is a local-first, cloud-ready code review platform for BCSE355L. It accepts Python and Java snippets, applies deterministic offline checks, persists reports in SQLite, and presents a developer-focused dashboard, history, analytics, settings, and finding details.

## Run locally

Prerequisites: Python 3.11+ with `pip`, and Node.js/npm. Run these commands from the repository root.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --app-dir backend --reload
```

In a second terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the Vite URL shown in the terminal (normally http://localhost:5173). The frontend currently calls the fixed local API origin `http://localhost:8000`; change the `API` constant in `frontend/src/main.tsx` before using a different backend origin.

API docs: http://localhost:8000/docs. Backend tests: `pytest backend/tests`. Frontend verification: `cd frontend; npm.cmd install; npm.cmd run build`.

## Safety and status

The default provider is `mock-demo`; no submitted code is executed, no credentials are required, and no AWS resources or paid inference are created. AWS SAM preparation and architecture notes are in `infra/` and `docs/`. Bedrock, authentication, DynamoDB repository parity, and browser automated tests remain cloud-hardening work before deployment. Do not deploy without reviewing [AWS cost safety](docs/AWS_COST_SAFETY.md).
