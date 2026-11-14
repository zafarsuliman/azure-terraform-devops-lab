# Interview Guide

## What problem does this solve?

It is a small work-tracking API used to demonstrate the full delivery path: validated application code, persistence, health semantics, container packaging, infrastructure as code and quality gates.

## Why this architecture?

FastAPI produces a clear typed contract. SQLite makes the local path immediate, while Azure Container Apps keeps hosting operationally light. The trade-off is that mounted SQLite is not a sound horizontally scaled transactional design, so PostgreSQL is the explicit production path.

## How does data move?

JSON requests are validated by Pydantic, handlers execute parameterised SQL within explicit transactions, SQLite persists to a mounted volume, and typed responses are serialised through FastAPI. Logs flow from stdout to Log Analytics.

## How are failures handled?

Validation returns 422, missing resources return 404, failed transactions roll back, readiness returns 503 on database failure, and correlation IDs connect responses to logs. CI stops promotion when lint, tests, dependency audit, image build or Terraform validation fails.

## How is security implemented?

Inputs are bounded and SQL is parameterised; the container is non-root; storage public access is disabled; Azure identity and least-scope CI permissions are used. Authentication is intentionally not claimed and is a required production improvement.

## How is it tested?

Tests use a disposable database and exercise operations, full CRUD, filtering, validation and missing records. CI also performs lint, dependency audit, image build, Terraform validation and Checkov scanning.

## What would change in production?

Use PostgreSQL, Alembic, OIDC authorization, remote encrypted Terraform state, Key Vault, private ingress, backups, alerts, SLOs, load testing and progressive revision traffic. Pin all actions and images by immutable digest for supply-chain assurance.
