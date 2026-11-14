import Lake
open Lake DSL

package «operator_lifts» where
  version := v!"0.1.0"

@[default_target]
lean_lib «OperatorLifts» where
  srcDir := "."
  roots := #[`Lifts, `Census]
