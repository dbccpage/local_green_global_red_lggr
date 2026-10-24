import Lake
open Lake DSL
package bell_positive_extensions
require rsi_mathlib_vendor from "vendor"
@[default_target]
lean_lib Bell where
  roots := #[`Bell]
  moreLeanArgs := #["-DwarningAsError=true"]
