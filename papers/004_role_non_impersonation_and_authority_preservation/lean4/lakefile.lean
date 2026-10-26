import Lake
open Lake DSL

package «role_non_impersonation» where
  version := v!"0.1.0"

@[default_target]
lean_lib «RoleNonImpersonation» where
  srcDir := "."
  roots := #[
    `RoleFailure,
    `ExceptionPipeline,
    `AuthorityResidual,
    `QuotientBoundary,
    `AuthorityDescent
  ]
