import Lake
open Lake DSL

package «LGGR3» where
  version := v!"1.5.1"
  buildDir := "b"

@[default_target]
lean_lib «LGGR3» where
  srcDir := "."
  roots := #[`Core]
