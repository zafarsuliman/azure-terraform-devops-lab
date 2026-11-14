# Security Policy

Do not report real credentials in an issue. Rotate any exposed secret immediately, remove it from reachable history, and contact the repository owner privately with reproduction details. Supported code is the latest `main` revision.

## Current review

- `pip-audit -r requirements.txt`: **PASS**, no known vulnerabilities found on 2 November 2026.
- Parameterised SQL, bounded Pydantic inputs, non-root container and read-only default CI permissions are implemented.
- Terraform validation, Checkov, container build and Trivy-style image inspection are **NOT VERIFIED locally** because Docker and Terraform are unavailable; CI defines validation and Checkov gates.
- Authentication and authorization are not implemented. Do not expose this sample to untrusted users or store sensitive data.
