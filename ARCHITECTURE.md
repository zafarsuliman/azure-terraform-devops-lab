# Architecture

## Decisions

- **FastAPI + Pydantic:** typed request contracts and generated OpenAPI reduce interface ambiguity.
- **SQLite locally:** zero-service onboarding and transactional writes suit this demonstration. The single-writer and shared-file constraints make PostgreSQL the recommended production migration.
- **Repository layer kept explicit:** parameterised SQL makes data flow inspectable and avoids hiding transaction boundaries.
- **Azure Container Apps:** managed container hosting, revisions, probes, scaling and Log Analytics integration without a Kubernetes control plane.
- **Azure Files mount:** persists the demonstration database across revisions. Public network access is disabled and the storage key is handled as a sensitive provider value, although a managed database is the stronger production design.

## Request and failure flow

Requests receive a correlation ID, validation occurs before handlers, SQL parameters prevent injection, transactions roll back on exceptions, and consistent HTTP errors describe invalid or missing resources. Readiness checks the database path; liveness checks only the process. Structured logs include method, route, status and latency without request bodies.

## Security boundaries

The container runs as a non-root user. Terraform enables TLS 1.2 minimum, private storage networking, managed identity and resource tags. CI receives read-only repository permission by default; production uses an environment gate and should use Azure workload identity federation rather than secrets. The sample lacks end-user authentication and must not be internet-exposed with sensitive data.

## Scale path

Move persistence to PostgreSQL with Alembic migrations, add OAuth2/OIDC and per-tenant authorization, restrict ingress behind Front Door/WAF, use Key Vault and private endpoints, enable backups/alerts, and test load plus disaster recovery.
