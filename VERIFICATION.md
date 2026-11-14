# Verification

Verified locally on 14 November 2026 from a clean project working directory.

| Check | Command | Result |
| --- | --- | --- |
| API tests | `.clean-venv\Scripts\python.exe -m pytest -q` | PASS - 3 tests |
| Static analysis | `.clean-venv\Scripts\python.exe -m ruff check app tests` | PASS |
| Docker runtime | `docker build` / `docker run` | NOT VERIFIED in the current environment |
| Azure deployment | `terraform apply` | NOT VERIFIED and intentionally not run |

The test run emitted a Starlette/httpx deprecation warning. It did not fail the tests, but dependency compatibility should be reviewed before treating this as production-ready. Terraform evidence in the portfolio report covers formatting, provider initialization, validation and Checkov without provisioning resources.
