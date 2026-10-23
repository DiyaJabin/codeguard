# Testing

Backend tests use FastAPI TestClient and SQLite and never call AWS. Run `pytest backend/tests`. The frontend verification command is `npm.cmd run build`; in this environment it is currently blocked by a missing optional Rolldown native binding.
