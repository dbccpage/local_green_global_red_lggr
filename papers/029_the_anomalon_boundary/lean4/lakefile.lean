import Lake
open Lake DSL

package «anomalon_boundary» where
  version := v!"0.1.0"

@[default_target]
lean_lib «AnomalonBoundary» where
  srcDir := "."
  roots := #[
    `OntologyBasic,
    `FiniteBoundary,
    `Census
  ]
