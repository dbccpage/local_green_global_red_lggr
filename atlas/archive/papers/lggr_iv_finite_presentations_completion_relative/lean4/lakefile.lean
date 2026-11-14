import Lake
open Lake DSL

package «LGGR4» where
  version := v!"0.1.0"
  buildDir := "b"

@[default_target]
lean_lib «LGGR4» where
  srcDir := "."
  roots := #[
    `core,
    `check_axioms
  ]
