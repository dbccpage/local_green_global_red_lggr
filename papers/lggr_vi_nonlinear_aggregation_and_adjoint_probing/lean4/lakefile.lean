import Lake
open Lake DSL

package «lggr_vi» where
  version := v!"0.1.0"

@[default_target]
lean_lib «LGGRVI» where
  srcDir := "."
  roots := #[`Core]
