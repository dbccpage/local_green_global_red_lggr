import Lake
open Lake DSL

package «constraint_regulation» where
  version := v!"0.1.0"

@[default_target]
lean_lib «ConstraintRegulation» where
  srcDir := "."
  roots := #[`Regulate, `Census]
