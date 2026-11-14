import Lake
open Lake DSL

package «finite_authority» where
  version := v!"0.1.0"

@[default_target]
lean_lib «FiniteAuthority» where
  srcDir := "."
  roots := #[`FiniteAuthority, `Census]
