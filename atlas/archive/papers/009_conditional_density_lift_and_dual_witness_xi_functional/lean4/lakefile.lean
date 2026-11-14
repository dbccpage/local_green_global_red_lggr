import Lake
open Lake DSL

package «conditional_density_lift» where
  version := v!"0.1.0"

@[default_target]
lean_lib «ConditionalDensityLift» where
  srcDir := "."
  roots := #[`Xi, `Census]
