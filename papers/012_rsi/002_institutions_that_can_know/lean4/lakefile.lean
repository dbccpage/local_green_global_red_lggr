import Lake
open Lake DSL

package «institutions_that_can_know» where
  version := v!"0.1.0"

@[default_target]
lean_lib «Core» where
  srcDir := "."
  roots := #[`Core]
