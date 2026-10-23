# CodeGuard AI — Project Handover

## Purpose and current status

CodeGuard AI is a local-first code-review demonstration for BCSE355L. It accepts Python and Java snippets or source-file uploads, runs deterministic offline pattern checks, stores reports in SQLite, and displays history, analytics, findings, settings, and demo status in a React dashboard.

The safe local path is the supported path today:

- `AI_PROVIDER=mock`
- `AWS_DEPLOY_ENABLED=false`
- `BEDROCK_ENABLED=false`
- SQLite at `./codeguard.db`
- No submitted code is executed
- No AWS resources or paid inference calls are created by the local app

The directory was not initialized as a Git repository during this audit. Therefore there are no local Git-tracked files, untracked-file records, or Git history available to inspect. Initialize Git only after reviewing the exclusions and the files listed under “Do not upload.”

## Project structure

```text
backend/
  app/
    api/routes.py          FastAPI endpoints and validation
    core/config.py         Environment-backed settings
    db.py                  SQLAlchemy engine/session setup
    main.py                FastAPI app, CORS, health endpoint, Lambda adapter
    models/review.py       Review persistence model and serialization
    providers/mock.py      Deterministic offline analyzer
    providers/bedrock.py   Explicitly disabled Bedrock placeholder
  requirements.txt
  tests/test_api.py
frontend/
  src/main.tsx             React UI and API calls
  src/styles.css           Dashboard styling
  package.json              Vite/React scripts and dependencies
infra/template.yaml        AWS SAM scaffold
docs/                      Architecture, AWS safety, deployment, testing, demo notes
samples/                   Safe Python and Java demonstration inputs
```

## Frontend

The frontend is a Vite React/TypeScript single-page application. It provides dashboard metrics, a code editor, Python/Java selection, local file upload, review results, history deletion, analytics, settings, and an about page. It calls `http://localhost:8000` directly from `frontend/src/main.tsx`; there is no frontend environment-variable or production API-origin configuration yet.

Run it from `frontend/` with `npm.cmd install` and `npm.cmd run dev`. A production-style verification is `npm.cmd run build`. The package’s `test` script is only a smoke placeholder and does not run browser tests.

## Backend

The backend is FastAPI with SQLAlchemy. Startup creates the SQLite schema. Configuration is loaded from `.env` through Pydantic Settings, with safe local defaults. CORS defaults to `http://localhost:5173`. The `mangum` adapter exposes `handler` for a Lambda deployment, but the cloud storage and cloud configuration are not implemented in the application.

The mock provider detects a small set of patterns: credential-like assignments, Python bare `except`, Python mutable defaults, Java empty catches, and Java direct console output. Findings are suggestions, not verified vulnerabilities.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Returns service health, environment, and configured provider |
| GET | `/api/config` | Returns non-secret runtime configuration and supported languages |
| POST | `/api/reviews` | Validates and analyzes a JSON review request |
| POST | `/api/reviews/upload` | Accepts a UTF-8 `.py` or `.java` upload, up to 100 KB |
| GET | `/api/reviews` | Lists paginated reviews; supports `search` and `severity` filters |
| GET | `/api/reviews/{review_id}` | Returns one saved review |
| DELETE | `/api/reviews/{review_id}` | Deletes one saved review |
| GET | `/api/stats` | Returns aggregate review, severity, category, language, and time statistics |

Interactive API documentation is available at `/docs` when the backend is running.

## Current AWS implementation

`infra/template.yaml` is an AWS SAM template containing:

- An API Gateway HTTP API.
- One Python 3.12 Lambda function using `app.main.handler`.
- A pay-per-request DynamoDB table keyed by `review_id`.
- A Lambda DynamoDB CRUD policy.
- Conservative defaults that keep Bedrock and deployment flags disabled.

The template is not a complete production deployment. Its CORS origin is `https://example.invalid`, and the application still uses the SQLAlchemy SQLite repository even when packaged for Lambda. The DynamoDB table is not wired into the backend. The frontend is not packaged or hosted by the template.

## Missing AWS/cloud components

Before any deployment, the teammate should design and review:

- A DynamoDB repository implementation and configuration switch, with schema/access-pattern tests and migration/data-retention decisions.
- Real API CORS configuration and a frontend API-origin configuration mechanism.
- Authentication and authorization, preferably Cognito/JWT or an approved alternative; the current API has no auth.
- IAM least-privilege review beyond the scaffold, including logs and any future secret access.
- CloudWatch log retention, metrics, alarms, and request/error observability.
- Frontend hosting and delivery, such as S3/CloudFront, with TLS, cache policy, and invalidation strategy.
- CI/CD, dependency pinning/update policy, environment separation, and rollback procedure.
- Input/rate limits, abuse protection, request logging redaction, and review-data privacy/retention policy.
- Bedrock integration only after model access, region, quotas, prompt/data handling, cost controls, and failure behavior are approved. The current Bedrock provider intentionally raises an error and is not callable.
- SAM validation, packaging, change-set review, account/region verification, budgets, and teardown verification.

Do not treat the SAM template as proof that the application is deployment-ready.

## Local setup

Prerequisites are Python 3.11+ with `pip`, Node.js/npm, and PowerShell on Windows. From the repository root:

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

The frontend normally runs at `http://localhost:5173`; the API normally runs at `http://localhost:8000`. Do not commit the copied `.env` file. The local SQLite database is generated at runtime and is ignored.

## Testing status

Backend tests are in `backend/tests/test_api.py` and use FastAPI `TestClient` plus a separate local SQLite test database. Run:

```powershell
pytest backend/tests
```

Frontend verification is currently a Vite production build:

```powershell
cd frontend
npm.cmd run build
```

There are no browser end-to-end tests, no AWS integration tests, no DynamoDB repository tests, no auth tests, and no Bedrock tests. The test module performs database setup at import time and should be isolated from any real database before expanding the suite.

## Deployment requirements

Deployment requires an explicitly verified AWS account and region, configured credentials held outside the repository, a real frontend origin, authentication, a cloud persistence implementation, reviewed IAM, logging/retention, budgets, and a cost/change-set review. Validate first with `sam validate --template-file infra/template.yaml`; do not deploy solely because the template validates. Review `docs/AWS_COST_SAFETY.md`, `docs/AWS_DEPLOYMENT.md`, and `docs/AWS_TEARDOWN.md` before any AWS action.

## Do not upload

The following must stay local or be generated after checkout:

- `.env` and any other environment files containing real values.
- AWS CLI credential/config directories and files, access keys, secret keys, session tokens, private keys, certificates, and local SAM/Terraform state.
- `.venv/`, `node_modules/`, caches, coverage output, build output, logs, editor settings, and OS metadata.
- `codeguard.db` and `test_codeguard.db`; these are local databases and may contain review code, filenames, or other user data. They are ignored but currently exist in the working directory and must not be selected during the first upload.
- Any future exports, dumps, screenshots, or logs containing submitted source or user data.

The sample source files, `.env.example`, application source, tests, docs, lockfile, and SAM template are intended project content, subject to the unresolved risks below.

## Publication risk assessment

**Not yet safe to publish without a final pre-upload review.** No credential values or secret-like filenames were found by the content/filename scan performed during this audit, and no Git history exists locally to scan. However, the repository was not initialized, so that result does not replace a final `git status`/`git ls-files` audit after initialization.

Resolved preparation items:

- `.gitignore` now covers environment files, the `.env.example` exception, databases, Python/Node artifacts, AWS/SAM/Terraform state, key/certificate extensions, credentials/config names, logs, caches, and machine-specific files.
- README setup instructions now include prerequisites, environment-file creation, the frontend API-origin limitation, and build verification.

Unresolved risks:

- No authentication or authorization exists.
- The frontend hardcodes the local API URL.
- Cloud Lambda deployment still uses SQLite in the application; DynamoDB is scaffolded but unused.
- The SAM CORS origin is a placeholder and the frontend is not deployed by the template.
- AWS/Bedrock integration, cost controls, quotas, prompt controls, and operational monitoring are not complete.
- No browser, cloud integration, security, dependency, or load testing is present.
- Existing local database files must be excluded from the upload even though the ignore rule now covers them.

If secrets are discovered in Git history after Git is initialized, removing them from the current files is insufficient. Revoke/rotate the affected credentials first, then rewrite repository history with an approved process and force-push only after coordinating with all collaborators.
