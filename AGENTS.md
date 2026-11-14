# Contributor Guidance

Work in small, reviewable changes. Never run `terraform apply` or `destroy` without explicit owner approval and a reviewed plan. Keep secrets out of code, state and logs. Add tests for behaviour changes, use parameterised SQL, preserve API compatibility where practical, and record checks actually run. Treat `.tfstate`, `.tfvars` and local databases as sensitive/generated files.

Definition of done: formatting and lint pass, tests cover success and failure paths, Terraform is formatted and validated where tooling exists, security findings are investigated, and documentation describes operational impact and rollback.
