# Two-minute demo

## Before the interview

Start Uvicorn, open `/docs`, and keep the Terraform files and GitHub Actions workflow open. Do not run `terraform apply` for the demo.

## 0:00–0:20 — Frame the problem

“This is a small persistent task API designed to show the path from application code to controlled Azure infrastructure—not to claim a live cloud deployment.”

## 0:20–0:55 — Show the application contract

Use Swagger UI to create, read, update, and delete a task. Show validation on an invalid request, then call `/health` and `/ready`. Point out request IDs and structured logs.

## 0:55–1:30 — Show infrastructure decisions

Walk through the Container App, private Azure Files persistence, Log Analytics, resource tags, and least-privilege identity configuration. Explain why SQLite is acceptable for a single-instance lab but PostgreSQL is the production scaling path.

## 1:30–1:50 — Show delivery safety

Show CI steps for linting, tests, dependency audit, image build, Terraform validation, and Checkov. Explain the production-environment gate, immutable image digest, rollback, and separate data-restoration concern.

## 1:50–2:00 — State the boundary

Close with: “No Azure resource was provisioned. The next production steps are OIDC, reviewed remote state, private ingress, backup validation, and a managed relational database.”

## Do not claim

- Terraform validation, Docker build, Checkov, and Azure deployment are not locally verified unless separately recorded.
- No cost, performance, uptime, or deployment outcome has been measured.
- The deployment job is a controlled placeholder until Azure OIDC is configured.

